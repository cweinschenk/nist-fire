#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
from pylab import *

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

#  =================
#  = User Settings =
#  =================

# Location of experimental data files
data_dir = '../Experimental_Data/'

# Location of file with timing information
timings_file = '../Experimental_Data/All_Hose_Times.csv'

# Location of scaling conversion files
scaling_file_default = '../DAQ_Files/Delco_DAQ_Channel_List.csv'
scaling_file_master = '../DAQ_Files/Master_DelCo_DAQ_Channel_List.csv'
scaling_file_west = '../DAQ_Files/West_DelCo_DAQ_Channel_List.csv'
scaling_file_east = '../DAQ_Files/East_DelCo_DAQ_Channel_List.csv'
results_loc = '../Experimental_Data/'

# Location of test description file
info_file = '../Experimental_Data/Description_of_Experiments.csv'
# Hose description file
hose_info_file = '../Experimental_Data/Description_Hose_Experiments.csv'

# Duration of pre-test time for bi-directional probes and heat flux gauges (s)
pre_test_time = 60

# List of sensor groups for each plot
sensor_groups = [['TC_A1_'], ['TC_A2_'], ['TC_A3_'], ['TC_A4_'], ['TC_A5_'],
                 ['TC_A6_'], ['TC_A7_'], ['TC_A8_'], ['TC_A9_'], ['TC_A10_'],
                 ['TC_A11_'], ['TC_A12_'], ['TC_A13_'], ['TC_A14_'], ['TC_A15_'],
                 ['TC_A16_'], ['TC_A17_'], ['TC_A18_'], ['TC_A19_'],
                 ['TC_Ignition'],
                 ['TC_Helmet_'],
                 ['BDP_A4_'], ['BDP_A5_'], ['BDP_A6_'], ['BDP_A7_'],
                 ['BDP_A8_'], ['BDP_A9_'], ['BDP_A10_'], ['BDP_A11_'],
                 ['BDP_A12_'], ['BDP_A13_'], ['BDP_A14_'], ['BDP_A15_'],
                 ['BDP_A18_'],
                 ['HF_', 'RAD_'],
                 ['GAS_', 'CO_', 'CO2_', 'O2_'],
                 ['HOSE_']]

# Common quantities for y-axis labelling
heat_flux_quantities = ['HF_', 'RAD_']
gas_quantities = ['CO_', 'CO2_', 'O2_']

# Load exp. timings, description, and averages file
timings = pd.read_csv(timings_file, index_col=0)
desired_tests = list(timings.columns.values)			# creates list of  column headers which
hose_info = pd.read_csv(hose_info_file, index_col=0) 	# correspond to desired tests
info = pd.read_csv(info_file, index_col=3)

# Files to skip
skip_files = ['_times', '_reduced', '_results', 'description_']

#creates lists for results file
stream_id = []
channel_id = []
fix_avg = []
sweep_avg = []
CW_avg = []
CCW_avg = []

#  ===============================
#  = Loop through all data files =
#  ===============================

for f in os.listdir(data_dir):
	if f.endswith('.csv'):
		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		# Strip test name from file name
		test_name = f[:-4]
		print 'Test ' + test_name

		# Skips undesired tests
		if test_name not in desired_tests:
			continue

		# Load exp. data file
		data = pd.read_csv(data_dir + f, index_col=0)

		# Load exp. scaling file
		if 'West' in test_name:
			scaling_file = scaling_file_west
		elif 'East' in test_name:
			scaling_file = scaling_file_east
		else:
			scaling_file = scaling_file_default

		scaling = pd.read_csv(scaling_file, index_col=2)

		# Read in test times to offset plots 
		start_of_test = info['Start of Test'][test_name]
		end_of_test = info['End of Test'][test_name]

		# Offset data time to start of test
		t = data['Time'].values - start_of_test

		# Save converted time back to dataframe
		data['Time'] = t

		#  ============
		#  = Plotting =
		#  ============

		# Generate a plot for each quantity group
		for group in sensor_groups:
			# Skips all groups not in "included groups" in hose_info file
			if any([substring in group for substring in hose_info['Included Groups'][test_name].split('|')]) == False:
				continue

			# sets stream data frames to emply
			SS_df = pd.DataFrame()
			
			


			# Defines start and end times for different stream patterns
			for stream in hose_info.columns[2:5]:
				# ignores streams not involved in test (specified in hose_info file)
				if stream[test_name] == 'NaN':
					continue

				start_name = stream + '_start'
				start = hose_info[start_name][test_name]
				end_name = stream + '_end'
				end = hose_info[end_name][test_name]

				# Creates data set for specific hose stream
				stream_data = data.iloc[start:end]
				t_stream = stream_data['Time']

				# Creates empty data frame (with time index) to plot average of channels for each stream and sensor group
				stream_group = pd.DataFrame(t_stream)

				for channel in stream_data.columns[1:]:
					# Skip excluded channels listed in hose_info file
					if any([substring in channel for substring in hose_info['Excluded Channels'][test_name].split('|')]):
						continue

					if any([substring in channel for substring in group]):

						calibration_slope = float(scaling['Calibration Slope'][channel])
						calibration_intercept = float(scaling['Calibration Intercept'][channel])

						# Plot velocities
						if 'BDP_' in channel:
							plt.rc('axes', color_cycle=['k', 'b', 'r', 'b', '0.75', 'c', 'm', 'y'])
							conv_inch_h2o = 0.4
							conv_pascal = 248.8

							# Convert voltage to pascals
							# Get zero voltage from pre-test data
							zero_voltage = np.mean(stream_data[channel][0:pre_test_time])
							pressure = conv_inch_h2o * conv_pascal * (stream_data[channel] - zero_voltage)

							# Calculate velocity
							quantity = 0.0698 * np.sqrt(np.abs(pressure) * (stream_data['TC_' + channel[4:]] + 273.15)) * np.sign(pressure)
							ylabel('Velocity (m/s)', fontsize=20)
							line_style = '-'
							axis_scale = 'Y Scale BDP'

						# # Plot hose pressure
						# if 'HOSE_' in channel:
						# 	plt.rc('axes', color_cycle=['k', 'r', 'g', 'b', '0.75', 'c', 'm', 'y'])
						# 	# Skip data other than sensors on 2.5 inch hoseline
						# 	if '2p5' not in channel:
						# 		continue
						# 	quantity = stream_data[channel] * calibration_slope + calibration_intercept
						# 	ylabel('Pressure (psi)', fontsize=20)
						# 	line_style = '-'
						# 	axis_scale = 'Y Scale HOSE'

						# Save converted quantity back to exp. dataframe and sensor group dataframe
						stream_data[channel] = quantity
						stream_group[channel] = quantity

				# Calculates the average of all channels in sensor group 
				group_avg = []
				for index, row in stream_group.iterrows():
					avg = np.mean(row[1:])
					group_avg.append(avg)

				# Adds a column of the average of all channels to the dataframe 
				stream_group['Average of Channels'] = group_avg

				# Saves dataframe based on stream 
				if stream == 'SS':
					SS_df = stream_group
				if stream == 'NF':
					NF_df = stream_group
				if stream == 'WF':
					WF_df = stream_group

				# Creates dataframe for each type of stream and type of pattern
				multi_fact = 0
				for diff in hose_info['Difference'][test_name].split('|'):

					multi_fact = multi_fact + 1
					name = 
					if stream == 'SS':
						SS_df = stream_sensor_group
						SS_fix = SS_df.iloc[0:180]
						SS_sweep = SS_df.iloc[240:420]
						SS_CW = SS_df.iloc[480:660]
						SS_CCW = SS_df.iloc[720:900]
						SS_CW_CCW = SS_df.iloc[480:900]
						SS_avg = stream_sensor_group['Sensor Average']
					if stream == 'NF':
						NF_df = stream_sensor_group
						NF_fix = NF_df.iloc[0:180]
						NF_sweep = NF_df.iloc[240:420]
						NF_CW = NF_df.iloc[480:660]
						NF_CCW = NF_df.iloc[720:900]
						NF_CW_CCW = NF_df.iloc[480:900]
						NF_avg = stream_sensor_group['Sensor Average']
					if stream == 'WF':
						WF_df = stream_sensor_group
						WF_fix = WF_df.iloc[0:180]
						WF_sweep = WF_df.iloc[240:420]
						WF_CW = WF_df.iloc[480:660]
						WF_CCW = WF_df.iloc[720:900]
						WF_CW_CCW = WF_df.iloc[480:900]
						WF_avg = stream_sensor_group['Sensor Average']

					multi_fact = multi_fact + 1
					if stream == 'SS':

					if stream == 'NF':

					if stream == 'WF':


                stream_id.append(stream)
                channel_id.append(channel)
        #Saves result file with averages
        results = {'Stream':stream_id, 'Channel':channel_id, 'Fixed':fix_avg, 'Sweeping':sweep_avg, 
            'CW':CW_avg, 'CCW':CCW_avg}
        results_file = pd.DataFrame(results, columns = ['Stream', 'Channel', 'Fixed', 'Sweeping', 
            'CW', 'CCW'])
        results_file.to_csv(results_loc + 'Hose_Test_results.csv')
        print 'Saved results'
        close('all')
        print

            # Plots sensor group channel average for each hose stream
            fig = figure()
            t = arange(len(quantity.index))

            plot(t, SS_avg, lw=1.5, ls='-', label= str(group)[2:-2] + 'SS_avg')
            plot(t, NF_avg, lw=1.5, ls='-', label= str(group)[2:-2] + 'NF_avg')
            plot(t, WF_avg, lw=1.5, ls='-', label= str(group)[2:-2] + 'WF_avg')

            # Scale y-axis limit based on specified range in test description file
            if axis_scale == 'Y Scale BDP':
                low = axis_scale + ' Low'
                high = axis_scale + ' High'
                ylim([-np.float(hose_info[low][test_name]), np.float(hose_info[high][test_name])])
            else:
                ylim([0, np.float(hose_info[axis_scale][test_name])])

            # Set axis options, legend, tickmarks, etc.
            ax1 = gca()
            xlim(0, len(SS_avg))
            ax1.xaxis.set_major_locator(MaxNLocator(8))
            ax1_xlims = ax1.axis()[0:2]
            ax1.axhspan(0, 0, color='0.50', lw=1)
            #grid(True)
            xlabel('Time', fontsize=20)
            ylabel('Velocity (m/s)', fontsize=20)
            xticks(fontsize=16)
            yticks(fontsize=16)
            legend(loc='lower right', fontsize=8)

            try:
                # Add vertical lines for timing information (if available)
                for index, row in timings.iterrows():
                    if pd.isnull(row[test_name]):
                        continue
                    axvline(index - start_of_test, color='0.50', lw=1)

                # Add secondary x-axis labels for timing information
                ax2 = ax1.twiny()
                ax2.set_xlim(ax1_xlims)
                ax2.set_xticks(timings[test_name].dropna().index.values - (start_of_test+60))
                setp(xticks()[1], rotation=60)
                ax2.set_xticklabels(timings[test_name].dropna().values, fontsize=8, ha='left')
                xlim(0, len(SS_avg))

                # Increase figure size for plot labels at top
                fig.set_size_inches(8, 8)
            except:
                pass

            # Save plot to file
            print 'Plotting ' + str(group)[1:-1] + ' Channel Average'
            savefig('../Figures/Hose_Test_Figures/' + test_name + '_' + str(group)[2:-2] + 'Avg.pdf')
            close('all')


            # Plots each individual channel of sensor group for each hose stream
############ Straight Stream ############
            fig = figure()
            t = arange(len(quantity.index))
            plt.rc('axes', color_cycle=['k', 'r', 'g', 'b', '0.75', 'c', 'm', 'y'])

            for channel in SS_df.columns[:]:
                
                # Plots sensor data columns
                if any([substring in channel for substring in group]):
                    plot(t, SS_df[channel], lw=1.5, ls='-', label=scaling['Test Specific Name'][channel])
            
            # Scale y-axis limit based on specified range in test description file
            if axis_scale == 'Y Scale BDP':
                low = axis_scale + ' Low'
                high = axis_scale + ' High'
                ylim([-np.float(hose_info[low][test_name]), np.float(hose_info[high][test_name])])
            else:
                ylim([0, np.float(hose_info[axis_scale][test_name])])

            # Set axis options, legend, tickmarks, etc.
            ax1 = gca()
            xlim(0, len(SS_avg))
            ax1.xaxis.set_major_locator(MaxNLocator(8))
            ax1_xlims = ax1.axis()[0:2]
            ax1.axhspan(0, 0, color='0.50', lw=1)
            #grid(True)
            xlabel('Time', fontsize=20)
            ylabel('Velocity (m/s)', fontsize=20)
            xticks(fontsize=16)
            yticks(fontsize=16)
            legend(loc='lower right', fontsize=8)

            try:
                # Add vertical lines for timing information (if available)
                for index, row in timings.iterrows():
                    if pd.isnull(row[test_name]):
                        continue
                    axvline(index - start_of_test, color='0.50', lw=1)

                # Add secondary x-axis labels for timing information
                ax2 = ax1.twiny()
                ax2.set_xlim(ax1_xlims)
                ax2.set_xticks(timings[test_name].dropna().index.values - (start_of_test+60))
                setp(xticks()[1], rotation=60)
                ax2.set_xticklabels(timings[test_name].dropna().values, fontsize=8, ha='left')
                xlim(0, len(SS_avg))

                # Increase figure size for plot labels at top
                fig.set_size_inches(8, 8)
            except:
                pass

            # Save plot to file
            print 'Plotting ' + str(group)[1:-1] + ' for SS'
            savefig('../Figures/Hose_Test_Figures/' + test_name + '_' + str(group)[2:-2] + 'SS.pdf')
            close('all')

############ Narrow Fog ############
            fig = figure()
            t = arange(len(quantity.index))
            plt.rc('axes', color_cycle=['k', 'r', 'g', 'b', '0.75', 'c', 'm', 'y'])
            
            for channel in NF_df.columns[:]:
                
                # Plots sensor data columns
                if any([substring in channel for substring in group]):
                    plot(t, NF_df[channel], lw=1.5, ls='-', label=scaling['Test Specific Name'][channel])

            # Scale y-axis limit based on specified range in test description file
            if axis_scale == 'Y Scale BDP':
                low = axis_scale + ' Low'
                high = axis_scale + ' High'
                ylim([-np.float(hose_info[low][test_name]), np.float(hose_info[high][test_name])])
            else:
                ylim([0, np.float(hose_info[axis_scale][test_name])])

            # Set axis options, legend, tickmarks, etc.
            ax1 = gca()
            xlim(0, len(SS_avg))
            ax1.xaxis.set_major_locator(MaxNLocator(8))
            ax1_xlims = ax1.axis()[0:2]
            ax1.axhspan(0, 0, color='0.50', lw=1)
            #grid(True)
            xlabel('Time', fontsize=20)
            ylabel('Velocity (m/s)', fontsize=20)
            xticks(fontsize=16)
            yticks(fontsize=16)
            legend(loc='lower right', fontsize=8)

            try:
                # Add vertical lines for timing information (if available)
                for index, row in timings.iterrows():
                    if pd.isnull(row[test_name]):
                        continue
                    axvline(index - start_of_test, color='0.50', lw=1)

                # Add secondary x-axis labels for timing information
                ax2 = ax1.twiny()
                ax2.set_xlim(ax1_xlims)
                ax2.set_xticks(timings[test_name].dropna().index.values - (start_of_test+60))
                setp(xticks()[1], rotation=60)
                ax2.set_xticklabels(timings[test_name].dropna().values, fontsize=8, ha='left')
                xlim(0, len(NF_avg))

                # Increase figure size for plot labels at top
                fig.set_size_inches(8, 8)
            except:
                pass

            # Save plot to file
            print 'Plotting ' + str(group)[1:-1] + ' for NF'
            savefig('../Figures/Hose_Test_Figures/' + test_name + '_' + str(group)[2:-2] + 'NF.pdf')
            close('all')

############ Wide Fog ############
            fig = figure()
            t = arange(len(quantity.index))
            plt.rc('axes', color_cycle=['k', 'r', 'g', 'b', '0.75', 'c', 'm', 'y'])
            
            for channel in WF_df.columns[:]:
                
                # Plots sensor data columns
                if any([substring in channel for substring in group]):
                    plot(t, WF_df[channel], lw=1.5, ls='-', label=scaling['Test Specific Name'][channel])

            # Scale y-axis limit based on specified range in test description file
            if axis_scale == 'Y Scale BDP':
                low = axis_scale + ' Low'
                high = axis_scale + ' High'
                ylim([-np.float(hose_info[low][test_name]), np.float(hose_info[high][test_name])])
            else:
                ylim([0, np.float(hose_info[axis_scale][test_name])])

            # Set axis options, legend, tickmarks, etc.
            ax1 = gca()
            xlim(0, len(SS_avg))
            ax1.xaxis.set_major_locator(MaxNLocator(8))
            ax1_xlims = ax1.axis()[0:2]
            ax1.axhspan(0, 0, color='0.50', lw=1)
            #grid(True)
            xlabel('Time', fontsize=20)
            ylabel('Velocity (m/s)', fontsize=20)
            xticks(fontsize=16)
            yticks(fontsize=16)
            legend(loc='lower right', fontsize=8)

            try:
                # Add vertical lines for timing information (if available)
                for index, row in timings.iterrows():
                    if pd.isnull(row[test_name]):
                        continue
                    axvline(index - start_of_test, color='0.50', lw=1)

                # Add secondary x-axis labels for timing information
                ax2 = ax1.twiny()
                ax2.set_xlim(ax1_xlims)
                ax2.set_xticks(timings[test_name].dropna().index.values - (start_of_test+60))
                setp(xticks()[1], rotation=60)
                ax2.set_xticklabels(timings[test_name].dropna().values, fontsize=8, ha='left')
                xlim(0, len(NF_avg))

                # Increase figure size for plot labels at top
                fig.set_size_inches(8, 8)
            except:
                pass

            # Save plot to file
            print 'Plotting ' + str(group)[1:-1] + ' for WF'
            savefig('../Figures/Hose_Test_Figures/' + test_name + '_' + str(group)[2:-2] + 'WF.pdf')
            close('all')

######### Plot of CW to CCW for average of each sensor group for each stream #########
            fig = figure()
            t = arange(len(SS_CW_CCW.index))
            plt.rc('axes', color_cycle=['k', 'b', 'r'])
            
            plot(t, SS_CW_CCW['Sensor Average'], lw=1.5, ls='-', label= 'SS_avg')
            plot(t, NF_CW_CCW['Sensor Average'], lw=1.5, ls='-', label= 'NF_avg')
            plot(t, WF_CW_CCW['Sensor Average'], lw=1.5, ls='-', label= 'WF_avg')

            # Set axis options, legend, tickmarks, etc.
            ax1 = gca()
            xlim(0, len(SS_CW_CCW))
            ax1.xaxis.set_major_locator(MaxNLocator(8))
            ax1_xlims = ax1.axis()[0:2]
            ax1.axhspan(0, 0, color='0.50', lw=1)
            grid(True)
            xlabel('Time', fontsize=20)
            ylabel('Velocity (m/s)', fontsize=20)
            xticks(fontsize=16)
            yticks(fontsize=16)
            legend(loc='lower right', fontsize=8)

            try:
                # Add vertical lines for timing information (if available)
                for index, row in timings.iterrows():
                    if pd.isnull(row[test_name]):
                        continue
                    axvline(index - start_of_test, color='0.50', lw=1)

                # Add secondary x-axis labels for timing information
                ax2 = ax1.twiny()
                ax2.set_xlim(ax1_xlims)
                ax2.set_xticks(timings[test_name].dropna().index.values - (start_of_test+60))
                setp(xticks()[1], rotation=60)
                ax2.set_xticklabels(timings[test_name].dropna().values, fontsize=8, ha='left')
                xlim(0, len(SS_CW_CCW))

                # Increase figure size for plot labels at top
                fig.set_size_inches(8, 8)
            except:
                pass

            # Save plot to file
            print 'Plotting CW vs CCW for ' + str(group)[1:-1]
            savefig('../Figures/Hose_Test_Figures/' + test_name + '_' + str(group)[2:-2] + 'Avg_CW_vs_CCW.pdf')
            close('all')