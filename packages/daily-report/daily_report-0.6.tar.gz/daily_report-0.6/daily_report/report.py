import numpy as np
import glob
import os
import sys
import logging
import warnings
import json
import matplotlib.pyplot as plt
import pandas as pd

from scipy import stats
from scipy.optimize import minimize
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from pathlib import Path

#####################

__version__ = "1.0"

HIDDEN_FILE_NAME = ".session_data.json"

warnings.simplefilter("error") # Used so that numpy warnings raise exceptions

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG) # Uncomment this line if you want to see the script's progress in the terminal

#####################

def parse_dataframe(df):
    """ Parses the BPOD dataframe to extract the session information and the results """
    
    # invalid_flag will be one for those sessions where invalid trials weren't taken into account
    invalid_flag = 0

    ##############################
    # Gather session metadata:
    ##############################
    try:
        box = df[df.MSG == 'SETUP-NAME']['+INFO'].iloc[0]
    except IndexError:
        box = "Unknown box"
        logging.warning("Box name not found.")
        
    try:
        session_name = df[df.MSG == 'SESSION-NAME']['+INFO'].iloc[0]
    except IndexError:
        session_name = "Unknown session"
        logging.warning("Session name not found. Saving as 'Unknown session'.")

    try:
        subject_name = df[df.MSG == 'SUBJECT-NAME']['+INFO'].iloc[0]
        subject_name = subject_name[1:-1].split(',')[0].strip("'")
    except IndexError:
        subject_name = "Unknown subject"
        logging.warning("Subject name not found.")
        
    try:
        session_started = df[df.MSG == 'SESSION-STARTED']['+INFO'].iloc[0]
        date = session_started.split()
        time = date[1][0:8]
        day = date[0]
    except IndexError:
        session_started = "??"
        time = "??"
        day = "??"
        logging.warning("Session start time not found.")
        
    try:
        stage_number = df[df.MSG == 'STAGE_NUMBER']['+INFO'].iloc[0]
        stage_number = int(stage_number)
    except IndexError:
        stage_number = np.nan
        logging.warning("Stage number not found.")

    metadata = {'box': box, 'session_name': session_name, 'subject_name': subject_name, 'time': time, 'day': day,
                'stage_number': stage_number}
    logging.info("Session metadata loaded. Continuing...") 

    ##############################
    # Gather session results:
    ##############################

    # length is necessary because sometimes the csv file ends with a trial where all states are Nan
    # it indicates the total number of trials that the animal completed (whether correct, incorrect or invalid)
    length = np.sum(df[df['MSG'] == 'StartSound']['BPOD-FINAL-TIME'].apply(lambda x: not np.isnan(float(x))).values)
    if length == 0:
        logging.critical("Session results not found; report can't be generated. Exiting...")
        sys.exit(1)
    # results contains True if the answer was correct, False otherwise:
    results = df[df['MSG'] == 'Punish']['BPOD-FINAL-TIME'].apply(lambda x: np.isnan(float(x))).values[:length]
    # invalids contains False for invalid trials and True otherwise
    invalids = df[df['MSG'] == 'Invalid']['BPOD-FINAL-TIME'].apply(lambda x: np.isnan(float(x))).values[:length]
    if not invalids.size:
        invalids = [True] * length
        invalid_flag = 1
        logging.warning("This session didn't take invalid trials into account.")
    # reward_side contains a 1 if the correct answer was the (R)ight side, 0 otherwise:
    try:
        reward_side = df[df.MSG == 'REWARD_SIDE']['+INFO'].iloc[-1][1:-1].split(',')[:length]
    except IndexError: # Compatibility with old files
        logging.warning("REWARD_SIDE vector not found. Trying old VECTOR_CHOICE...")
        try:
            reward_side = df[df.MSG == 'VECTOR_CHOICE']['+INFO'].iloc[-1][1:-1].split(',')[:length]
        except IndexError:
            logging.critical("Neither REWARD_SIDE nor VECTOR_CHOICE found. Exiting...")
            sys.exit(1)
    # Cast to int from str:
    reward_side = [int(x) for x in reward_side]
    # Response times for the session and its mean:
    response_time = df[df.MSG == 'WaitResponse']['+INFO'].values[:length]
    if response_time.size:
        response_time = response_time.astype(float)
        if invalid_flag:
            response_time = invalids * response_time # Don't take invalid trials into account
        response_time = [x > 0 and x < 3 for x in response_time] * response_time # Remove outliers
        response_time = int(np.mean(response_time) * 1000)
    else:
        response_time = np.nan
        logging.info("No response time found; it is undefined from now on.")
    # coherences vector, from 0 to 1 (later it will be converted into evidences from -1 to 1):
    coherences =  df[df['MSG'] == 'coherence01']['+INFO'].values[:length]
    coherences = coherences.astype(float)
    if not coherences.size:
        logging.info("This trial doesn't use coherences.")
    
    session_results = {'length': np.asscalar(length), 'results': results, 'invalids': invalids, 
                       'invalid_flag': invalid_flag, 'reward_side': reward_side, 
                       'response_time': response_time, 'coherences': coherences}

    logging.info("Session results loaded. Continuing...")

    return metadata, session_results    

def compute_trial_info(length, len_performance, binary_perf, invalid_flag):
    """ Extracts the information concerning trials: number of correct and invalid, percentage of total and total water """
    
    invalid_trials = length - len_performance
    correct_trials = binary_perf.count(1)
    correct_trials_per_cent = round(correct_trials * 100 / length, 2)
    if invalid_flag:
        invalid_trials = np.nan
    else:
        invalid_trials = length - len_performance
    invalid_trials_per_cent = round(invalid_trials * 100 / length, 2)
    
    # Each correct trial implies 24 uL of water; we display it in mL in the report
    water = round(correct_trials * 0.024, 3)

    trial_info = {'correct_trials': correct_trials, 'correct_trials_per_cent': correct_trials_per_cent, 
                  'invalid_trials': invalid_trials, 'invalid_trials_per_cent': invalid_trials_per_cent,
                  'water': water}

    return trial_info

def compute_window(data):
    """ Computes a rolling average with a length of 20 samples """
    performance = []
    for i, elem in enumerate(data):
        if i < 20: 
            performance.append(round(np.mean(data[0:i+1]), 2))
        else:
            performance.append(round(np.mean(data[i-20:i]), 2))
    return performance

def compute_performances(reward_side, results, invalids):
    """ Computes total, left and right performances as well as the indices of each """
    
    # For the performance display, take into account that invalid trials do not count towards
    # overall performance; hence, the indices of the non-invalid trials must be tracked for the displays
    # and calculations.
    
    perf_indices = [] # indices of non-invalid trials, starting at 1
    binary_perf = [] # contains 1 if the trial was correct, 0 otherwise
    left_indices = [] # indices of the (L)eft side trials
    left_trials = [] # contains 1 if the trial was correct, 0 otherwise (only left channel)
    right_indices = [] # indices of the (R)ight side trials
    right_trials = [] # contains 1 if the trial was correct, 0 otherwise (only right channel) 

    for i, elem in enumerate(reward_side):
        if invalids[i] == True:
            perf_indices.append(i+1)
            binary_perf.append(results[i])
            if elem == 0: 
                left_indices.append(i+1)
                left_trials.append(results[i])
            else: 
                right_indices.append(i+1)
                right_trials.append(results[i])
    
    # We need to check for the eventuality that a session consists only on
    # left side or  right side trials.
    if not left_indices:
        logging.info("This trial consisted only on right side stimuli.")
        total_L_performance = np.nan
        left_performance = []
        corrects_on_left = np.nan
    else:
        total_L_performance = np.asscalar(round(np.mean(left_trials), 2))
        left_performance = compute_window(left_trials)
        corrects_on_left = left_trials.count(1)
        
    if not right_indices:
        logging.info("This trial consisted only on left side stimuli.")
        total_R_performance = np.nan
        right_performance = []
        corrects_on_right = np.nan
    else:
        total_R_performance =  np.asscalar(round(np.mean(right_trials), 2))
        right_performance = compute_window(right_trials)
        corrects_on_right = right_trials.count(1)

    performance = compute_window(binary_perf) 
    total_performance =  np.asscalar(round(np.mean(performance), 2))

    performances = {'binary_perf': binary_perf, 'perf_indices': perf_indices, 'performance': performance, 
                    'left_indices': left_indices, 'right_indices': right_indices, 'left_performance': left_performance, 
                    'right_performance': right_performance, 'total_R_performance': total_R_performance, 
                    'total_L_performance': total_L_performance, 'total_performance': total_performance,
                    'corrects_on_left': corrects_on_left, 'corrects_on_right': corrects_on_right}

    return performances

def psychometric_curve(coherences, reward_side, results):
    """ Computes the psychometric curve fit, the data error and the fit parameters """
    
    def R_resp(reward_side, results):
        r_resp = []
        for i, elem in enumerate(results):
            if reward_side[i] == elem: r_resp.append(1)
            else: r_resp.append(0)
        return r_resp

    def sigmoid_MME(params):

        k = params[0]
        x0 = params[1]   
        B = params[2]
        P = params[3]

        yPred = B+(1-B-P)/(1 + np.exp(-k*(xdata-x0)))

        # Calculate negative log likelihood
        LL = -np.sum( stats.norm.logpdf(ydata, loc=yPred) )
        return(LL)

    evidences = [(2*x-1) for x in coherences]
    R_resp = R_resp(reward_side, results)
    a = {'R_resp': R_resp, 'evidence': evidences, 'coh': coherences}
    coherence_dataframe = pd.DataFrame(a)

    info = coherence_dataframe.groupby(['evidence'])['R_resp'].mean()
    ydata = info.values
    xdata = info.index.values
    err = coherence_dataframe.groupby(['coh'])['R_resp'].sem()
    LL = minimize(sigmoid_MME, [1,1,0,0])

    k = LL['x'][0]
    x0 = LL['x'][1]
    B = LL['x'][2]
    P = LL['x'][3]

    fit = B+(1-B-P)/(1 + np.exp(-k*(np.linspace(-1,1,30)-x0)))

    psychometric_curve = {'xdata': [np.asscalar(x) for x in xdata], 'ydata': [np.asscalar(x) for x in ydata], 
                          'fit': list(fit), 'params': [np.asscalar(x) for x in LL['x']], 'err': list(err)}
    
    return psychometric_curve

def manage_directories(subject_name):    
    """ If necessary, it creates the daily_reports file inside the HOME folder and the animal subdir. """
    
    if not os.path.exists(os.path.expanduser("~/daily_reports/")): 
        os.makedirs(os.path.expanduser("~/daily_reports/"))
        logging.info("Daily_report directory not found. Creating it...")
    if not os.path.exists(os.path.expanduser("~/daily_reports/" + subject_name)): 
        os.makedirs(os.path.expanduser("~/daily_reports/" + subject_name))
        logging.info("Directory for this subject not found. Creating it...")
    os.chdir(os.path.expanduser("~/daily_reports/" + subject_name))
    
def make_daily_report(performances, session_results, trial_info, metadata, curve_data = []):
    """ Creates a daily report with the performance and psychometric plots, if necessary. """    
    
    with PdfPages(metadata['session_name'] + '.pdf') as pdf:
            plt.figure(figsize=(11.7, 8.3))
            axes1 = plt.subplot2grid((2,3), (0,0), colspan=3)
            axes1.set_ylim([0,1.1])
            axes1.set_yticks(list(np.arange(0,1.1, 0.1)))
            axes1.set_yticklabels(['0', '', '','','','50', '','','','','100'])
            axes1.set_title("Session accuracy")
            axes1.plot(performances['perf_indices'], performances['performance'], marker = 'o', markersize=2, color = 'black', linewidth = 0.7)
            if performances['left_indices']:
                axes1.plot(performances['left_indices'], performances['left_performance'], marker = 'o', markersize=2, color = 'cyan', linewidth = 0.7)
            if performances['right_indices']:
                axes1.plot(performances['right_indices'], performances['right_performance'], marker = 'o', markersize=2, color = 'magenta', linewidth = 0.7)
            axes1.set_xlim([1,session_results['length']+1])
            axes1.set_ylabel('[%]')
            axes1.set_xlabel('Trials')
            axes1.spines['right'].set_visible(False)
            axes1.spines['top'].set_visible(False)
            legend_elements = [Line2D([0], [0],color='black', label='Total'),
            Line2D([0], [0], color='cyan', label='Left'),
            Line2D([0], [0], color='magenta', label='Right')]
            leg = plt.legend(loc="lower right", handles=legend_elements, ncol=1, prop={'size': 8})
            leg.get_frame().set_alpha(0.5)
            
            if np.isnan(session_results['response_time']):
                response_time_str = "Not taken into account"
            else:
               response_time_str = str(session_results['response_time']) + ' ms'
               
            if performances['left_indices']:
               L_corrects_str =  f"Corrects on left: {performances['corrects_on_left']} ({round(performances['corrects_on_left'] * 100 / trial_info['correct_trials'], 1)} %)"
            else:
               L_corrects_str =  f"Corrects on left: N/A"
            
            if performances['right_indices']:
               R_corrects_str =  f"Corrects on right: {performances['corrects_on_right']} ({round(performances['corrects_on_right'] * 100 / trial_info['correct_trials'], 1)} %)"
            else:
               R_corrects_str =  f"Corrects on right: N/A"
               
            if np.isnan(trial_info['invalid_trials']):
                invalid_trials_str = "Not taken into account"
            else:
                invalid_trials_str = str(trial_info['invalid_trials']) + " (" + str(trial_info['invalid_trials_per_cent']) + "%)"
                
            s1 = f"Date: {metadata['day']} { metadata['time']}\n" 
            s2 = f"Subject name: {metadata['subject_name']} / Box: {metadata['box']}\n"  
            s3 = f"Total trials: {session_results['length']} / Correct trials: {trial_info['correct_trials']} ({trial_info['correct_trials_per_cent']} %) / {L_corrects_str} / {R_corrects_str}\n"
            s4 = f"Invalid trials: {invalid_trials_str} / Water: {trial_info['water']} mL / Mean response time: {response_time_str}"
            
            plt.text(0.02, 0.92, s1+s2+s3+s4, fontsize=8, transform=plt.gcf().transFigure)
            
            if curve_data:
                axes2 = plt.subplot2grid((2,3), (1,1), colspan=1)
                axes2.plot([0,0], [0, 1], 'k-', lw=1, linestyle=':')
                axes2.plot([-1, 1], [0.5, 0.5], 'k-', lw=1, linestyle=':')
                axes2.errorbar(curve_data['xdata'], curve_data['ydata'], yerr=curve_data['err'], fmt='ro', elinewidth = 1, markersize = 3)
                axes2.plot(np.linspace(-1,1,30), curve_data['fit'], color = 'black', linewidth = 1)
                axes2.set_yticks(np.arange(0, 1.1, step=0.1))
                axes2.set_title("Psychometric curve")
                axes2.set_xlabel('evidence')
                axes2.set_ylabel('R-prob')
                axes2.set_xlim([-1.05, 1.05])
                axes2.set_ylim([-0.05,1.05])
                axes2.tick_params(labelsize=9)
                axes2.annotate(str(round( curve_data['ydata'][0] ,2)), xy=(curve_data['xdata'][0], 
                             curve_data['ydata'][0]), xytext=(curve_data['xdata'][0]-0.03, 
                                       curve_data['ydata'][0]+0.05), fontsize = 8)
                axes2.annotate(str(round(curve_data['ydata'][-1],2)), xy=(curve_data['xdata'][-1], 
                             curve_data['ydata'][-1]), xytext=(curve_data['xdata'][-1]-0.1, 
                                       curve_data['ydata'][-1]-0.08), fontsize = 8)
                axes2.annotate("S = " + str(round(curve_data['params'][0],2)) + "\n" + "B = " +
                             str(round(curve_data['params'][1],2))+ "\n" + "LR_L = " + 
                             str(round(curve_data['params'][2],2))+ "\n" +"LR_R = " + 
                             str(round(curve_data['params'][3],2)), xy =(0,0), xytext = (-1,0.85), fontsize = 7 )
                plt.tight_layout()
                plt.subplots_adjust(top=0.85, hspace=0.3)             
            pdf.savefig(plt.gcf())  # saves the current figure into a pdf page
            plt.close()
            
            
    logging.info("Daily report done. Continuing...")

def read_hidden_file(session_info):
    """ Reads the hidden file with all the data, or creates it if it doesn't exist.
        Returns a list that contains the data of all past sessions. 
    """    
    file_path = Path(HIDDEN_FILE_NAME)
    if not file_path.exists():
        logging.info("Creating hidden file for the first time.")
        with open(HIDDEN_FILE_NAME, 'w+') as file:
            multi_session_info = [session_info]
            json.dump(multi_session_info, file, sort_keys=True, indent=4)
    else:
        with open(HIDDEN_FILE_NAME, 'r+') as file:
            logging.info("Existing record found.")
            multi_session_info = json.load(file)
            file.seek(0)
            multi_session_info.append(session_info)
            json.dump(multi_session_info, file, sort_keys=True, indent=4)
            file.truncate()

    return multi_session_info

def make_intersession_report(multi_session_info, subject_name):
    """ Creates an inter-session report with the data from all previous sessions. """
    
    def marker_color(stage_nums, default_color):
        marker_color = []
        colors = ['blue', 'green', 'red', 'orange']
        for number in stage_nums:
            if np.isnan(number):
                marker_color.append(default_color)
            else:
                marker_color.append(colors[number-1])
        return marker_color
    
    curve_indices = []
    response_times_plot = False
    
    # Calculate whether we will need some of the plots:
    for elem in multi_session_info:
        if not np.isnan(elem.get('response_time')):
            response_times_plot = True
            break
    # Calculate % of invalid trials:
    invalids_per_cent = [round(elem.get('invalid_trials') / elem.get('trial_num'), 1) if not np.isnan(elem.get('invalid_trials')) else np.nan for elem in multi_session_info]
    for i, elem in enumerate(multi_session_info):
        if elem.get('xdata') is not None:
            curve_indices.append(i)
    
    with PdfPages(subject_name + '_inter_session.pdf') as pdf:

        number_of_sessions = len(multi_session_info)
        if number_of_sessions <= 30:
            x_limit = 35
        else:
            x_limit = number_of_sessions + 2

        x = range(1,number_of_sessions+1)

        # FIRST PAGE (accuracy plots)

        plt.figure(figsize=(11.7, 8.3))
        axes1 = plt.subplot2grid((4,8), (0,0), colspan=7)
        axes1.set_xlim([0,x_limit])
        axes1.set_ylim([0,1.1])
        axes1.set_yticks(list(np.arange(0,1.1, 0.1)))
        axes1.set_yticklabels(['0', '', '','','','50', '','','','','100'])
        axes1.set_title("Session accuracy", fontsize = 11)
        
        # Scatter and plot for total performance:
        y = [session['total_perf'] for session in multi_session_info]
        total_color = marker_color([session['stage_number'] for session in multi_session_info], 'black')
        axes1.plot(x, y, color = 'black', linewidth=0.7, zorder = 1)
        axes1.scatter(x, y, c = total_color, s = 3, zorder = 2)
    
        # Scatter and plot for right side performance:
        y = [session['R_perf'] for session in multi_session_info]
        axes1.scatter(x, y, c = total_color, s = 3, zorder = 2)
        axes1.plot(x, y, color = 'magenta', linewidth=0.7, zorder = 1)
        
        # Scatter and plot for left side performance:
        y = [session['L_perf'] for session in multi_session_info]
        axes1.scatter(x, y, c = total_color, s = 3, zorder = 2)
        axes1.plot(x, y, color = 'cyan',  linewidth=0.7, zorder = 1)
        
        # Scatter and plot for invalid trials:
        axes1.scatter(x, invalids_per_cent, c = total_color, s = 3, zorder = 2)
        axes1.plot(x, invalids_per_cent, color = 'gray', zorder = 1, linewidth = 0.7, linestyle = 'dashed')

        axes1.set_ylabel('Accuracy [%]')
        axes1.set_xlabel('Session')
        axes1.spines['right'].set_visible(False)
        axes1.spines['top'].set_visible(False)
        plt.text(0.1, 0.95, "Subject name: " + subject_name, fontsize=8, transform=plt.gcf().transFigure)
        legend_elements = [Line2D([0], [0],color='black', label='Total'),
        Line2D([0], [0], color='cyan', label='Left'),
        Line2D([0], [0], color='magenta', label='Right'),
        Line2D([0], [0], color='gray', label='Inv %', linestyle = 'dashed')]
        leg = plt.legend(handles=legend_elements, ncol=1, prop={'size': 7}, bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
        leg.get_frame().set_alpha(0.5) 
        
        # Total trials plot:
        axes4 = plt.subplot2grid((4,8), (1,0), colspan=7)   
        axes4.set_xlim([0,x_limit])
        aux = [session['trial_num'] for session in multi_session_info]
        max_value = np.amax([x if not np.isnan(x) else -1 for x in aux])
        if max_value < 100:
            max_value = 100
        else:
            max_value = (max_value // 100) * 100 + 200
        axes4.set_ylim([0,max_value])
        axes4.set_title("Number of trials per session", fontsize = 11)
        axes4.plot(x, aux, color = 'black', linewidth=0.7, zorder = 1)
        axes4.scatter(x, aux, c = total_color, s = 3, zorder = 2)
        axes4.set_ylabel('Trials')
        axes4.set_xlabel('Session')
        axes4.spines['right'].set_visible(False)
        axes4.spines['top'].set_visible(False)
        
        plot_number = 2
        
        # Coherences 1 and -1 plot:
        if curve_indices:
            
            coh_neg = []
            coh_pos = []
            
            for elem in multi_session_info:
                ydata = elem.get('ydata')
                if ydata is None:
                    coh_neg.append(np.nan)
                    coh_pos.append(np.nan)
                else:
                    coh_neg.append(1-ydata[0])
                    coh_pos.append(ydata[-1])
         
            axes2 = plt.subplot2grid((4,8), (plot_number,0), colspan=7)
    
            axes2.set_xlim([0,x_limit])
            axes2.set_ylim([0,1.1])
            axes2.set_yticks(list(np.arange(0,1.1, 0.1)))
            axes2.set_yticklabels(['0', '', '','','','50', '','','','','100'])
            axes2.set_title("Session accuracy for evidences 1 and -1", fontsize = 11)

            axes2.plot(x, coh_neg, color = 'cyan', linewidth=0.7, zorder = 1)
            axes2.scatter(x, coh_neg, c = total_color, s = 3, zorder = 2)

            axes2.plot(x, coh_pos, color = 'magenta', linewidth=0.7, zorder = 1)
            axes2.scatter(x, coh_pos, c = total_color, s = 3, zorder = 2)

            axes2.spines['right'].set_visible(False)
            axes2.spines['top'].set_visible(False)
            legend_elements = [Line2D([0], [0], color='cyan', label='Left'),
            Line2D([0], [0], color='magenta', label='Right')]
            plt.legend(handles=legend_elements, ncol=1, prop={'size': 7}, bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
            axes2.set_ylabel('Accuracy [%]')
            axes2.set_xlabel('Session')
            
            plot_number += 1
        
        # Reponse times plot:
        if response_times_plot:

            axes3 = plt.subplot2grid((4,8), (plot_number,0), colspan=7)

            axes3.set_xlim([0,x_limit])
            aux = [session['response_time'] for session in multi_session_info]
            max_value = np.amax([x if not np.isnan(x) else -1 for x in aux])
            if max_value < 400:
                axes3.set_ylim([0,500])
            else:
                axes3.set_ylim([0,max_value+100])
            axes3.set_title("Session mean response times", fontsize = 11)
            y = [session['response_time'] for session in multi_session_info]
            axes3.plot(x, y, color = 'black', linewidth=0.7, zorder = 1)
            axes3.scatter(x, y, c = total_color, s = 3, zorder = 2)
            axes3.set_ylabel('Response time [ms]')
            axes3.set_xlabel('Session')
            axes3.spines['right'].set_visible(False)
            axes3.spines['top'].set_visible(False)
         
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.9, bottom = 0.1, top = 0.9)
        pdf.savefig()  # saves the current figure into a pdf page
        plt.close() 
        
        if curve_indices:        
            # REST OF PAGES (psychometric plots in A4 paper, landscape, 12 plots per page)
            sessions_with_curve = []
            for elem in curve_indices:
                sessions_with_curve.append(multi_session_info[elem])                
            for ii, session in enumerate(sessions_with_curve):
                if ii % 12 == 0:
                    plt.figure(figsize=(11.7, 8.3))
                plt.subplot2grid((3,4), ((ii % 12) // 4, ii % 4), colspan=1)
                plt.plot(np.linspace(-1,1,30), session['fit'], linewidth=0.8, c = 'black')
                plt.errorbar(session['xdata'],
                             session['ydata'], 
                             yerr=session['fit_error'], fmt='ro', markersize = 3, elinewidth = 0.7)
                plt.plot([0,0], [0, 1], 'k-', lw=1, linestyle=':')
                plt.plot([-1, 1], [0.5, 0.5], 'k-', lw=1, linestyle=':')
                plt.xlim([-1.05, 1.05])
                plt.ylim([-0.05,1.05])
                plt.xlabel('Evidence')
                plt.ylabel('R-prob')
                plt.title(' '.join((session['day'], '(Session', str(curve_indices[ii]+1) + ')')), fontsize =10)
                if (ii % 12 == 11) or len(sessions_with_curve)-1 == ii: # If we finished the page or we reached the last plot
                    plt.tight_layout()
                    plt.subplots_adjust(left = 0.1, right = 0.9, bottom = 0.1, top = 0.9)
                    pdf.savefig(plt.gcf())  # saves the current figure into a pdf page
                    plt.close()

def main(datafile_path):
    
    logging.info("Initializing report script.")

    try:
        #df = pd.read_csv(glob.glob("*.csv")[0], skiprows=6, sep=';') # Uncomment this line for manual editing of CSV files
        df = pd.read_csv(datafile_path, skiprows=6, sep=';')
    except FileNotFoundError:
        logging.critical("CSV file not found. Exiting...")
        sys.exit(1)
        
    metadata, session_results = parse_dataframe(df)

    logging.info("Starting daily report for subject " + metadata['subject_name'])
    
    performances = compute_performances(session_results['reward_side'], session_results['results'], session_results['invalids'])
    invalids_flag = session_results['invalid_flag'] # for clarity
    trial_info = compute_trial_info(session_results['length'], len(performances['performance']), performances['binary_perf'], invalids_flag)
    manage_directories(metadata['subject_name'])
    
    # psycho_flag tells the program to not print the psychometric curve for that session,
    # neither in the daily nor in the inter-session report. As of now, the curve is not plotted when
    # there aren't coherences in the session or when the session only consists on left or right side trials.
    psycho_flag = bool(len(session_results['coherences'])) and not np.isnan(performances['total_L_performance']) and not np.isnan(performances['total_R_performance'])
    
    # Data to be written into the hidden file:
    session_info = {'trial_num': session_results['length'], 'correct_trials': trial_info['correct_trials'],
                   'invalid_trials': trial_info['invalid_trials'], 'total_perf': performances['total_performance'],
                   'L_perf': performances['total_L_performance'], 'R_perf': performances['total_R_performance'], 'day': metadata['day'], 
                   'response_time': session_results['response_time'], 'stage_number': metadata['stage_number']}
    if psycho_flag:
        curve_data = psychometric_curve(session_results['coherences'], session_results['reward_side'], session_results['results'])
        session_info['xdata'] = curve_data['xdata'] 
        session_info['ydata'] = curve_data['ydata'] 
        session_info['fit_error'] = curve_data['err']   
        session_info['fit'] = curve_data['fit']
        make_daily_report(performances, session_results, trial_info, metadata, curve_data)
    else:
        make_daily_report(performances, session_results, trial_info, metadata) 
        
    multi_session_info = read_hidden_file(session_info)
    
    logging.info("Starting inter-session report.")
    
    make_intersession_report(multi_session_info, metadata['subject_name'])  
    
    logging.info("Inter-session report done. All finished!")   
    
if __name__ == "__main__": main("test_files/data.csv")

