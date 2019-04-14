% use this script to convert rhd files with all 32 ch saved to a .dat file
% for clustering
clear


%% specify parameters and paths

dataPath = uigetdir('Z:/GintyLab/Emanuel/Data','Choose folder with .rhd files');
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
    
    if exist('board_adc_data')
        aiFileName = strcat(filename(1:end-4),'AnalogInputs.mat');
        save(aiFileName,'board_adc_data') % save analog inputs
    end
    
    %% writing only the channels for the tetrode to the file
    if size(amplifier_data,1) == 32
        fwrite(fid, amplifier_data([25 17 1 9],:),'int16'); % append to .dat file
        %the order of the channels matches tetrode-LLO-new.prb
    else
        newAmpData = zeros(4,size(amplifier_data,2));
        for j = 1:size(amplifier_data,1)
            channelNum = str2num(amplifier_channels(j).native_channel_name(end-2:end));
            if channelNum == 24
                newAmpData(1,:) = amplifier_data(j,:);
            elseif channelNum == 16
                newAmpData(2,:) = amplifier_data(j,:);
            elseif channelNum == 0
                newAmpData(3,:) = amplifier_data(j,:);
            elseif channelNum == 8
                newAmpData(4,:) = amplifier_data(j,:);
            end
        end
        
        fwrite(fid, newAmpData,'int16'); % append this to the .dat file instead
    end
                
                
 
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


