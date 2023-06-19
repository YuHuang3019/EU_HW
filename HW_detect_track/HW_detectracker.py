class HeatwaveTracker:
    def __init__(self, yr, all_lat, all_lon, T, thres, s, N, M, L, overlap_threshold, consecutive_days):
        """
        Initialize HeatwaveTracker object.
        
        Args:
        - yr: year.
        - T: 3D array of temperature data in the form of (day, lat, lon).
        - thres: 3D array of temperature threshold data in the form of (day, lat, lon).
        - s: sliding window size.
        - N: integer threshold for the number of hot pixels in a sliding window to be considered a heatwave event.
        - M: integer threshold for the number of hot pixels in a minimum coverage heatwave.
        - L: float distance threshold in degrees for two heatwave events on consecutive days to be considered the same event.
        - overlap_threshold: float overlap threshold (in terms of area or indicies) for two heatwave events on consecutive days to be considered the same event.
        - consecutive_days: the minimum lasting duration of one heatwave event.
        """
        # all_lat, all_lon, T, thres, s, N, M, L, overlap_threshold, consecutive_days = glb.hyperparams
        self.T = T
        self.thres = thres
        self.all_lat = all_lat
        self.all_lon = all_lon
        self.s = s
        self.N = N
        self.M = M
        self.L = L
        self.overlap_threshold = overlap_threshold
        self.consecutive_days = consecutive_days
        
        # Initialize internal variables for _process_day
        self.current_hot_indice = {} # dictionary containing current day non-isolate hot pixel indices, key is day
        self.current_center = {} # dictionary containing center location (lat, lon) of current day (day is the key value in self.current_hot_indice)
        self.current_intensity = {} # dictionary containing mean and max T values over the hot pixels of current day (day is the key value in self.current_hot_indice)
        
        # Initialize internal variables for _merge_events 
        self.events = {} # dictionary of heatwave events start, end days and durations
        

        
    def _process_day(self, day):
        """
        Process each single day of temperature data to detect hot pixels and remove isolated/sparse hot anomalies.
        
        Args:
        - day: integer representing the (current) day to process.
        
        Outputs:
        - self.current_hot_indice
        
        """
        # Generate boolean mask of hot pixels for current day
        hot_pixels = self.T[day] > self.thres[day] # np.where(self.T[day] > self.thres[day], 1, 0)
        hot_indicies = np.arange(0, hot_pixels.shape[0]*hot_pixels.shape[1]).reshape([hot_pixels.shape[0],hot_pixels.shape[1]])
        hot_indicies = hot_indicies*hot_pixels.astype(int)
        new_hot_indice = np.array([0])
        
        # Loop over sliding windows
        for i in range(self.T.shape[1]-15):
            for j in range(self.T.shape[2]-15):
                # Check if sliding window contains enough hot pixels to be considered as a non-anomalies event
                if hot_pixels[i:i+s, j:j+s].sum() >= self.N:
                    tmp_new_hot_indice = hot_indicies[i:i+s, j:j+s].reshape(-1)
                    new_hot_indice = np.unique(np.append(new_hot_indice, tmp_new_hot_indice))            
            
        new_hot_indice = new_hot_indice[new_hot_indice != 0]

        # Set a minimum total hot pixel coverage area - about the area of 1/2 France
        if (len(new_hot_indice) > self.M):
            #calculate the center location, mean and max T values
            clat = np.mean(all_lat[np.isin(hot_indicies, new_hot_indice)])
            clon = np.mean(all_lon[np.isin(hot_indicies, new_hot_indice)])
        
            meanT = np.mean(T[day][np.isin(hot_indicies, new_hot_indice)])
            maxT = np.max(T[day][np.isin(hot_indicies, new_hot_indice)])
            
            self.current_center[day] = (clat, clon)
            self.current_intensity[day] = meanT, maxT
            self.current_hot_indice[day] = new_hot_indice 

    
    
    def _satis_distance_or_overlap_criteria(self, end_day, day):
        # For day and day+1, calculate the center distance
        R = 6371.0  # Approximate radius of earth in km
        lat1, lon1  = self.current_center[end_day]
        lat2, lon2 = self.current_center[day]
        lat1 = np.radians(lat1)
        lat2 = np.radians(lat2)
        lon1 = np.radians(lon1)
        lon2 = np.radians(lon2)
        dlon = np.abs(lon1 - lon2)
        dlat = np.abs(lat1 - lat2)

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * math.atan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c
                  
        # Calculate the area overlap ratio
        setA = set(self.current_hot_indice[end_day])
        setB = set(self.current_hot_indice[day])
        overlap = setA & setB
        smaller_set = np.min([len(setA), len(setB)])
        overlap_ratio = float(len(overlap) / smaller_set)
           
        # Meetinge one criteria would be enough
        if (overlap_ratio >= self.overlap_threshold) or (distance <= L):
            return True
        else:
            return False
        
                                  
                    
    def _merge_events(self, ):
        # For one hw event, the starting and ending day
        start_day = 0
        end_day = 0
        duration = 0
        last_day = list(self.current_hot_indice)[-1] # last day with non-isolated hot pixels in this year
        current_event = False # If there is an existing event 
        current_event_id = 0 # ID of current heatwave event
        
        # Only days with hot pixels that satisfies the _process_day function would be looped here
        for day in self.current_hot_indice.keys():
            
            # If currently, the new day is not within an existing hw event current_event = False, then start a hw event
            # Attention: use ~ True instead of ! True
            if (not current_event) and (day < last_day - 1):
                start_day = day
                end_day   = day
                duration = end_day - start_day + 1
                current_event = True
                
            # If currently, the new day is within an existing hw event 
            elif current_event: 
                # If the current day and the end day from the event are consecutive
                if day == end_day + 1:
                    # Further check if the hw coverages in the two days overlap or the centers of hw coverages are within the distance L
                    criteria_check = self._satis_distance_or_overlap_criteria(end_day, day)
                    if criteria_check:
                        # Update the duration and end day info
                        end_day = day
                        duration = end_day - start_day + 1
                        # Finalize last event when reaching end of the days
                        if day == last_day:
                            current_event = False
                    else:
                        # Do not update duration and end day if the criteria is not met, just end the event
                        current_event = False      
                # If the new day and end day are not consecutive, end the hw event
                else:
                    current_event = False               
            
            # For the ended event, check if the hw duration is larger than the minimum required length
            if (duration > 0) and (not current_event):
                if duration >= 3:
                    current_event_id += 1
                    self.events[current_event_id] = {'start_day': start_day, 'end_day': end_day, 'duration': duration} 
                
                # If the event is not ended the last day (namaly, not consecutive or not merged not situations)
                # The current day needs to be counted as the first day of a new event
                start_day = day
                end_day   = day
                duration = end_day - start_day + 1
                current_event = True 
                
                
        
    def detect_heatwaves(self):
        """
        Detect heatwave events and track their movement across days.
        
        Returns:
        - events: dictionary containing all heatwave events
                  with keys as event IDs and values as dictionaries containing 
                  duration, start day, end day.
        """
        if __name__ == '__detect_heatwaves__':
              main()
        
        # Process each day to select hot pixels and remove the sparse isolated anomalies
        for day in range(self.T.shape[0]):
            self._process_day(day)
        
        # Loop all days from last step and merge the consecutive events that meet certain criteria
        if len(self.current_hot_indice) > 0:
            self._merge_events()
        
            # Merge the dictionaries current_hot_indice, current_center, and current_intensity info into events
            for id in self.events.keys():
                self.events[id]['center_lat'] = list( map(self.current_center.get, np.arange(self.events[id]['start_day'], self.events[id]['end_day']+1)) )
                self.events[id]['Tmean Tmax'] = list( map(self.current_intensity.get, np.arange(self.events[id]['start_day'], self.events[id]['end_day']+1)) )
        
            # Load pickle module and save the dictionary events         
            import pickle
            with open('/burg/glab/users/yh3019/csv/hw'+yr+'.pkl', "wb") as fp:
                pickle.dump(self.events, fp)  
                print(yr, ': HW event dictionary saved successfully to file')
        else:
            print(yr, ': No non-isolated hot pixels detected')
            
        # When returning, save the whole dictionary as the value to the year id (key is the str year) 
        yr_events = {yr: self.events}
        return yr_events
    
     