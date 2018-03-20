%% specify parameters and paths
clear
dataPath = uigetdir('Z:/HarveyLab/Tier1/Alan/Data','Choose folder with .rhd files');
rhdFiles = dir([dataPath '/*.rhd']); % list all rhd files
[~, idx] = sort({rhdFiles.date});
rhdFiles = rhdFiles(idx);
prb = 'poly2';
clusteringPath = 'C:/Users/Alan/Documents/Github/clustering-pipelines';
[~, basename, ~] = fileparts(dataPath);


%% Print names of files to check order
for i = 1:length(rhdFiles)
    fprintf('%s\n',rhdFiles(i).name) % print each file to make sure it's in order
    % need the sorting performed above!!!
end

%% 
mkdir(dataPath,'alldata')
dataFileName = [dataPath '\alldata\raw.dat']; % make .dat file
fid = fopen(dataFileName, 'w'); % open .dat file for writing

for i = 1:length(rhdFiles)
    fprintf('Loading file %i of %i, %s\n',i, length(rhdFiles),fullfile(dataPath,rhdFiles(i).name));
    read_Intan_RHD2000_file(fullfile(dataPath,rhdFiles(i).name),0);
    
    
    diFileName = strcat(filename(1:end-4),'DigitalInputs.mat');
    save(diFileName,'board_dig_in_data') % save digital inputs
    % when I make analog channel inputs, make a similar expression here
    
    fwrite(fid, amplifier_data(:),'int16'); % append to .dat file
    
    % cleanup
    if i < length(rhdFiles) %% don't clear for the last file so can use these for building prm file
        clear amplifier_channels amplifier_data aux_input_channels aux_input_data ...
        board_dig_in_data board_dig_in_channels filename frequency_parameters ...
        notes reference_channel spike_triggers supply_voltage_channels supply_voltage_data ...
        t_amplifier t_aux_input t_dig t_supply_voltage
    end
end

st = fclose('all');
fprintf('Finished\n')

%% Copy probe file to directory (for KlustaKwik clustering)

if strcmp(prb,'poly2')
    copyfile(fullfile(clusteringPath, 'Klusta', 'A1x32-Poly2-5mm-50s-177-A32.prb'), fullfile(dataPath,'alldata','A1x32-Poly2-5mm-50s-177-A32.prb'))
    prb_file = 'A1x32-Poly2-5mm-50s-177-A32.prb';
end

prmFile = fullfile(dataPath,'alldata',[basename '.prm']);
fid2 = fopen(prmFile, 'wt');
fprintf(fid2,"experiment_name = '%s'\n",basename);
fprintf(fid2,"prb_file = '%s'\n",prb_file);
fprintf(fid2,'traces = dict( \n');
fprintf(fid2,"\traw_data_files = ['raw.dat'],\n"); % hard coded raw.dat, which should be the file name for all recordings made with this script
fprintf(fid2,'\tvoltage_gain = %.1f,\n',195); % from intan documentation
fprintf(fid2,'\tsample_rate = %.1f,\n',frequency_parameters.amplifier_sample_rate);
fprintf(fid2,'\tn_channels = %i,\n',length(amplifier_channels));
fprintf(fid2,"\tdtype = 'int16'\n");
fprintf(fid2,'\t)\n\n');

fprintf(fid2,'spikedetekt = dict(\n');
fprintf(fid2,'\tfilter_low = 500.,\n');
fprintf(fid2,'\tfilter_high_factor  = 0.95 * .5,\n'); % high pass filter (as documented in phy)
fprintf(fid2,'\tfilter_butter_order = 3,\n'); % order of Butterworth Filter
fprintf(fid2,'\n');
fprintf(fid2,'\tfilter_lfp_low=20,\n'); % LFP filter low-pass frequency
fprintf(fid2,'\tfilter_lfp_high=0,\n'); %LFP filter high-pass frequency
fprintf(fid2,'\n');
fprintf(fid2,'\tchunk_size_seconds=1,\n');
fprintf(fid2,'\tchunk_overlap_seconds=.015,\n');
fprintf(fid2,'\n');
fprintf(fid2,'\tn_excerpts=50,\n');
fprintf(fid2,'\texcerpts_size_seconds=1,\n');
fprintf(fid2,'\tthreshold_strong_std_factor=5.5,\n');
fprintf(fid2,'\tthreshold_weak_std_factor=3.5,\n');
fprintf(fid2,"\tdetect_spikes='negative',\n");
fprintf(fid2,'\n');
fprintf(fid2,'\tconnected_component_join_size=1,\n');
fprintf(fid2,'\n');
fprintf(fid2,'\textract_s_before=16,\n');
fprintf(fid2,'\textract_s_after=16,\n');
fprintf(fid2,'\n');
fprintf(fid2,'\tn_features_per_channel=3,\n'); %number of features per channel
fprintf(fid2,'\tpca_n_waveforms_max=10000,\n');
fprintf(fid2,')\n');
fprintf(fid2,'\n');
fprintf(fid2,'klustakwik2 = dict(\n');
fprintf(fid2,'\tnum_starting_clusters=100,\n');
fprintf(fid2,')\n');

st = fclose(fid2);
clear






