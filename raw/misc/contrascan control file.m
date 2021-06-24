function SFcontrascan(subNo)
% currently (10/10/19) 60 trials, 4166 ms per trial, ~860 sec. 440 TRs)
% Get the size of the on screen window: [screenXpixels, screenYpixels] = Screen('WindowSize', win);
% Screen('glTranslate',....
% Screen('glScale',...
% see: http://psychtoolbox.org/docs/DrawMirroredTextDemo

%%% ----------------------- PRE-SETTINGS ---------------------- %%%
 Screen('Preference', 'SkipSyncTests', 1);
clc;
rand('state', sum(100*clock));
% open serial port for trigger writing
    if ~strcmp(computer, 'MACI64')
    s3 = serial('COM3'); % on PC only
    fopen(s3)
    end
% Screen settings
screens=Screen('Screens');
screenNumber=max(screens);
HideCursor;
[w, wRect]=Screen('OpenWindow', screenNumber);
[center(1), center(2)] = RectCenter(wRect);
fix_cord = [center-5 center+5];
Screen('TextSize', w, 30);
% coloring pixel values
white = WhiteIndex(w);   % 255
black = BlackIndex(w);   % 0
gray = (white+black)/2;  % 127.5
inc = white-gray;        % 127.5
% define frequency
durationpic = 0.027;   % shooting for 13.33 Hz: w scanner monitor 12 hz
flickdur = 50;         % how long to flicker, 35 or 45 in Spatfreq       
puma = [];             % tic toc recording
% Gabor stuff
orientation = 45;
actfreqs = 14.2514; % what are these units??

% ------------ set number of trials with the ITI vector ------------ %
% make ITI vector:  there is already a 500 ms fixation dot screen   
% 30 trials:  itiVec = cat(1,4*ones(16,1), 6*ones(8,1), 8*ones(4,1), 16*ones(2,1));  
% 50 trials:  itiVec = cat(1,4*ones(26,1), 6*ones(13,1), 8*ones(7,1),16*ones(4,1)); %302 sec

itiVec = cat(1,4*ones(31,1), 6*ones(16,1), 8*ones(9,1), 16*ones(4,1)); % 60 trials, 356 sec

itiRand = itiVec(randperm(length(itiVec))); % shuffle the ITIs
spatfreq_conditions = ones(1,length(itiRand));  % only 1 condition for now   
spatfreq_conditions_rand = spatfreq_conditions;
spatialfrequency = actfreqs(spatfreq_conditions_rand(length(spatfreq_conditions))).*0.0025;
% spatfreq_conditions_rand = spatfreq_conditions(randperm(length(spatfreq_conditions))); 

[x,y] = meshgrid(-200:200, -200:200);
m = (exp(-((x/100).^2)-((y/100).^2)) .* sin(cos(orientation*pi/180)*(2*pi*spatialfrequency)*x + sin(orientation*pi/180)*(2*pi*spatialfrequency)*y));
% draw the Gabor one time outside of timing loop
Screen('PutImage', w, gray+inc*(0.005*exp(1/10)*m)); % max contrast 0.3299

% Define KeyPad/Response
KbName('UnifyKeyNames');

% datfile and file labelling
datafilename = strcat('SFcontraScan_',num2str(subNo),'.dat'); % name of data file to write to

% Prevent accidentally overwriting data (except for subject numbers > 99)
if subNo < 99 && fopen(datafilename, 'rt') ~= -1
    fclose('all');
    error('Result data file exists!');
else
    datafilepointer = fopen(datafilename, 'wt');
end
    
% ------------------- EXPERIMENT START ----------------------------  %                 
try
AssertOpenGL;
% set priority - also set after Screen init
priorityLevel=MaxPriority(w);
Priority(priorityLevel);

Screen('FillRect', w, gray)
 
%%%%%%%%%%%%%%%%%%%%%%% BEGIN EXPERIMENT %%%%%%%%%%%%%%%%%%%%%%%%
% Initial Welcome Screen
% vbl = Screen('Flip', w);
% tstart = vbl;
% time_timer = 10;   Timer does not work in scanner :(
%     while GetSecs < tstart + 11
%     DrawFormattedText(w, 'Experiment will begin in...', center(1)-200,center(2)-50, 255);
%     DrawFormattedText(w, num2str(time_timer), center(1),center(2), 255);
%     vbl  = Screen('Flip', w);
%     WaitSecs(1)
%     time_timer = time_timer-1;    
%     end  % welcome screen timer loop

% ----------------- First Flip and Mirror Text ------------------- %% 
% Make a backup copy of the current transformation matrix for later
% use/restoration of default state:
Screen('glPushMatrix', w);
% Translate origin into the geometric center:
Screen('glTranslate', w, center(1), center(2), 0);
%  scaling transform which flips the diretion of x-Axis
%  Screen('glScale', windowPtr, sx, sy [, sz]):  transform by (sx, sy, sz)
Screen('glScale', w, 1, -1, 3);
% We need to undo the translations...
Screen('glTranslate', w, -center(1), -center(2), 0);
% The transformation is ready for mirrored drawing of text:
Screen('DrawText', w, 'The experiment will begin soon...', center(1)-200,center(2)-50, 255);
% Restore to non-mirror mode, aka the default transformation
% that you've stored on the matrix stack:
Screen('glPopMatrix', w);
% Now all transformations are back to normal and we can proceed
Screen('Flip',w);

% --------------------- Non-flipped starting stuff ---------------- %
% DrawFormattedText(w, 'The experiment will begin soon...', center(1)-200,center(2)-50, 255);
% Screen('Flip', w); % show text
% wait for mouse presssca

buttons=0;
    while ~any(buttons) % wait for press
        [x,y,buttons] = GetMouse;
        % Wait 10 ms before checking the mouse again to prevent
        % overload of the machine at elevated Priority()
        WaitSecs(0.01);
    end

Screen('Flip', w); % clear screen
Screen('FillOval', w, uint8(black), fix_cord) %fills/colors fixation dot in center
Screen('Flip', w);
WaitSecs(4.000);

% conditions - make a phase loop if adding more conditions
% for phase = 1: ??, also uncomment end at line 162
phase=1;
% Trial and flicker loop
for trial = 1:length(spatfreq_conditions)
  % ---------------- questionable port stuff HERE %%%%%%%%%%%%%%
% ioObj = io64;
% % % initialize the interface to the inpoutx64 system driver
% status = io64(ioObj);
% % % if status = 0, you are now ready to write and read to a hardware port
% address = hex2dec('E020');     %standard LPT1 output port address
% data_out=0;                    %sample data value
% io64(ioObj,address,data_out);  %output command
% address = hex2dec('E030');     %standard LPT1 output port address
% data_out=0;                    %sample data value
% io64(ioObj,address,data_out);  %output command
% address = hex2dec('E020');     %standard LPT1 output port address
% data_out=2;                    %sample data value
% io64(ioObj,address,data_out);  %output command
% address = hex2dec('E030');     %standard LPT1 output port address
% data_out=2;                    %sample data value
% io64(ioObj,address,data_out);  %output command
% % % when finished with the io64 object it can be discarded via
% % % 'clear all', 'clear mex', 'clear io64' or 'clear functions' command.
% clear io64  
    
% ----------------------- Add breaks if making longer -------------- %
%     if trial == 100
%      % take a break
%         Screen('DrawText', w, 'Great JOB! Take a short break!  Press mouse key to resume ...', 10, 10, 255);
% 
%         Screen('Flip', w); % show text
% 
%         % wait for mouse press ( no GetClicks  :(  )
%         buttons=0;
%         while ~any(buttons) % wait for press
%         [x,y,buttons] = GetMouse;
%         % Wait 10 ms before checking the mouse again to prevent
%         % overload of the machine at elevated Priority()
%         WaitSecs(0.01);
%         end
%     end
Screen('FillOval', w, uint8(black), fix_cord) %fills/colors fixation dot in center
Screen('Flip', w);
WaitSecs(0.5);
% ------------------- for adding a conditioning portion ------------- %  
%     if phase ==2 && spatfreq_conditions_rand(trial) <3,  flickdur = 45;  
%     else flickdur = 35;
%     end

% Flicker loop
 if ~strcmp(computer, 'MACI64')
     serialbreak(s3,10), 
 end

tic                
  for flicker = 1:flickdur
  % Screen('PutImage', w, gray+inc*(0.005*exp(flicker/10)*m)); % max contrast 0.3299
   Screen('PutImage', w, gray+inc*(0.005*exp(flicker/11)*m)); % max contrast 0.3299
   Screen('FillOval', w, uint8(black), fix_cord) %fills/colors fixation dot in center
   Screen('Flip', w);
   WaitSecs(durationpic);
   Screen('FillOval', w, uint8(black), fix_cord) %fills/colors fixation dot in center
   Screen('Flip',w);
   WaitSecs(durationpic);
%     if phase ==2 && spatfreq_conditions_rand(trial) <3 && flicker == 36
%        play(p)
%     end
  end % flicker loop

puma = toc; % record length (ms) of trial

Screen('FillOval', w, uint8(black), fix_cord) %fills/colors fixation dot in center
Screen('Flip', w);  % remove gabor patch

    % Dat file information
    fprintf(datafilepointer,'%i %i %i %i %i \n', ...
    subNo, ...
    phase, ...
    trial, ...
    spatfreq_conditions_rand(trial), ...                   
    puma);                  

    WaitSecs(itiRand(trial))

end  % end trial loop
% write message to subject
Screen('glPushMatrix', w);
Screen('glTranslate', w, center(1), center(2), 0);
Screen('glScale', w, 1, -1, 3);
Screen('glTranslate', w, -center(1), -center(2), 0);
Screen('DrawText', w, 'Thank you very much for participating!',center(1)-320,center(2)-50, 255);
Screen('DrawText', w, 'Please remain still and wait for instructions...',center(1)-320,center(2), 255);
Screen('glPopMatrix', w);
Screen('Flip',w);
WaitSecs(8) 
% ------------------------ non-flipped end stuff -------------------- %
% Screen('DrawText', w, 'Thank you very much for participating!',center(1)-320,center(2)-50, 255);
% Screen('DrawText', w, 'Please remain still and wait for instructions...',center(1)-320,center(2), 255);
% Screen('Flip', w); % show text
% WaitSecs(8)    
     
% end % phase loop 
    
% End of Experiment, error catch

    catch
        Screen('CloseAll');
        ShowCursor;
        fclose('all');
        Priority(0);
        psychrethrow(psychlasterror);
          
end % try/catch loop

Screen('CloseAll');
ShowCursor;
fclose('all');
Priority(0);
     
