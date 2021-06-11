import glob, os

## We want to gloriously process each file in the folder labeled .vmrk, so we'll use a for loop
# grabs each file name ending in .vmrk and stores it as the string file_name
for file_name in glob.glob("*.vmrk"):
    # opens a connection to the file that we chose, named current_file
    with open(os.path.join(os.getcwd(), file_name), 'r') as current_file:
        # now convert the file into a list of lines
        line_list = current_file.read().splitlines()

        ## Go through each line and grab each presentation time, labeled as 'S  2', then store them in a list
        # initialize fmri start time and list of presentation times
        presentation_times = []
        fmri_start_time = 0
        # get fmri start time, which will be on the first line containing 'R128', between the second and third comma
        # nest the for loop like a champ
        for line in line_list:
            if 'R128' in line:
                fmri_start_time = float(line.split(",")[2])
                # now break our loop because we found the start time
                break
       
        ## time for the next loop! now we are getting the presentation times and adjusting them to the fmri start time
        for line in line_list:
            if 'S  2' in line:
                # grab the presentation time and add it to the list of presentation times
                # the presentation time is between the second and third comma
                presentation_time = float(line.split(",")[2])
                # notice that here we are subtracting the fmri start time from our presentation time
                # and dividing by 5000 to convert to seconds
                adjusted_presentation_time = (presentation_time - fmri_start_time) / 5000
                presentation_times.append(adjusted_presentation_time)

        ## Output the adjusted list of times into a text file, one time per line
        # make a new file named after the current target file
        writing_file_name = file_name[:-5] + ".onsets.txt"
        with open(os.path.join(os.getcwd(), writing_file_name), 'w') as writing_file:
            # commence writing the presentation times to the file
            for adjusted_presentation_time in presentation_times:
                writing_file.write(str(adjusted_presentation_time) + "\n")

        ## send some output to our anxiously awaiting user
        # divide fmri_start_time by five thousand to convert to seconds
        print(f"{file_name}: fMRI start time: {fmri_start_time / 5000}")
        print(f"{file_name}: Copied stimulus onset times to {writing_file_name}")

print("All times are subtracted by the time at which the fMRI began making images.")