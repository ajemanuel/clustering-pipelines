%% specify parameters and paths
clear

dataPath = uigetdir('Z:/HarveyLab/Tier1/Alan/Data','Choose folder with .rhd files');
tempPath = 'C:\\temp\';
%clusteringPath = 'C:/Users/Alan/Documents/Github/clustering-pipelines';

%cleaning up the tempPath in case anything is in it %% warning %%
delete([tempPath '*'])
delete([tempPath '\alldata\*'])
if exist([tempPath 'alldata'],'dir')
    rmdir([tempPath 'alldata'])
end

fprintf('copying files to temporary path on SSD\n')
copyfile([dataPath '\*.rhd'],tempPath)
rhdFiles = dir([tempPath '*.rhd']); % list all rhd files
[~, idx] = sort({rhdFiles.date});
rhdFiles = rhdFiles(idx);



%% Print names of files to check order
for i = 1:length(rhdFiles)
    fprintf('%s\n',rhdFiles(i).name) % print each file to make sure it's in order
    % need the sorting performed above!!!
end

%% 
mkdir(tempPath,'alldata')
dataFileName = [tempPath '\alldata\raw.dat']; % make .dat file
fid = fopen(dataFileName, 'w'); % open .dat file for writing

for i = 1:length(rhdFiles)
    fprintf('Loading file %i of %i, %s\n',i, length(rhdFiles),fullfile(tempPath,rhdFiles(i).name));
    read_Intan_RHD2000_file(fullfile(tempPath,rhdFiles(i).name),0);
    
    
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

fprintf('copying files back to server\n')
delete([tempPath '*.rhd'])
copyfile(tempPath,dataPath)

%cleaning up
delete([tempPath '\*'])
delete([tempPath '\alldata\*'])
rmdir([tempPath 'alldata'])

fprintf('Finished\nThe directory was %s\n',dataPath)
clear

