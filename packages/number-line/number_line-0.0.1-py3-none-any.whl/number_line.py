class NumberLine:

	global numbers
	import numbers
	
	def __init__(self):
		self.__ranges = []

#----Methods for User----
	def add_point(self, point_val):
		lower_val = point_val
		upper_val = point_val
		includes_lower_val = True
		includes_upper_val = True

		self.add_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
	
	def remove_point(self, point_val):
		lower_val = point_val
		upper_val = point_val
		includes_lower_val = True
		includes_upper_val = True

		self.remove_range(lower_val, includes_lower_val, upper_val, includes_upper_val)

	def contains_point(self, point_val):
		lower_val = point_val
		upper_val = point_val
		includes_lower_val = True
		includes_upper_val = True

		contains_point = self.contains_range_totally(lower_val, includes_lower_val, upper_val, includes_upper_val)
			
		return contains_point

	def add_range(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		is_valid_range = self.is_valid_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
		if is_valid_range:
			contains_range_totally = self.contains_range_totally(lower_val, includes_lower_val, upper_val, includes_upper_val)
			if not contains_range_totally:
				contains_range_partially = self.contains_range_partially(lower_val, includes_lower_val, upper_val, includes_upper_val)
				if contains_range_partially:
					overlapping_ranges = self.get_overlapping_ranges(lower_val, includes_lower_val, upper_val, includes_upper_val)
					merged_range_dict = self.merge_ranges(lower_val, includes_lower_val, upper_val, includes_upper_val, overlapping_ranges)
					for temp_range_dict in overlapping_ranges:
						temp_lower_val = temp_range_dict['lower value']
						temp_includes_lower_val = temp_range_dict['includes lower value']
						temp_upper_val = temp_range_dict['upper value']
						temp_includes_upper_val = temp_range_dict['includes upper value']
						self.remove_range(temp_lower_val, temp_includes_lower_val, temp_upper_val, temp_includes_upper_val)
					self.__ranges.append(merged_range_dict)
				else:
					range_dict = {
						'lower value': lower_val, 
						'upper value': upper_val,
						'includes lower value': includes_lower_val,
						'includes upper value': includes_upper_val
					}
					self.__ranges.append(range_dict)

	def remove_range(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		is_valid_range = self.is_valid_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
		if is_valid_range:
			range_dict = {
				'lower value': lower_val, 
				'upper value': upper_val,
				'includes lower value': includes_lower_val,
				'includes upper value': includes_upper_val
			}
			contains_range_totally = self.contains_range_totally(lower_val, includes_lower_val, upper_val, includes_upper_val)
			contains_range_exactly = self.contains_range_exactly(lower_val, includes_lower_val, upper_val, includes_upper_val)
			contains_range_partially = self.contains_range_partially(lower_val, includes_lower_val, upper_val, includes_upper_val)

			if contains_range_exactly:
				self.__ranges.remove(range_dict)
			elif contains_range_totally:
				overlapping_range = self.get_overlapping_ranges(lower_val, includes_lower_val, upper_val, includes_upper_val)
				overlapping_range_dict = overlapping_range[0]
				l_r_lower_val = overlapping_range_dict['lower value']
				l_r_upper_val = lower_val
				l_r_includes_lower_val = overlapping_range_dict['includes lower value']
				l_r_includes_upper_val = False
				lower_range = {
					'lower value': l_r_lower_val, 
					'upper value': l_r_upper_val,
					'includes lower value': l_r_includes_lower_val,
					'includes upper value': l_r_includes_upper_val
				}
				u_r_lower_val = upper_val
				u_r_upper_val = overlapping_range_dict['upper value']
				u_r_includes_lower_val = False
				u_r_includes_upper_val = overlapping_range_dict['includes upper value']
				upper_range = {
					'lower value': upper_val, 
					'upper value': u_r_upper_val,
					'includes lower value': u_r_includes_lower_val,
					'includes upper value': u_r_includes_upper_val
				}
				self.__ranges.remove(overlapping_range_dict)
				try:
					self.add_range(l_r_lower_val, l_r_includes_lower_val, l_r_upper_val, l_r_includes_upper_val)
				except ValueError:
					pass
				try:
					self.add_range(u_r_lower_val, u_r_includes_lower_val, u_r_upper_val, u_r_includes_upper_val)
				except ValueError:
					pass
			elif contains_range_partially:
				raise ValueError('Some of the values in the range you listed are not currently included in the number line')
			else:
				raise ValueError('Some of the values in the range you listed are not currently included in the number line')

	def get_ranges(self):
		return self.__ranges

	def print_number_line(self):
		ranges = self.__ranges

		for i in range(len(ranges)):
			curr_range = ranges[i]
			curr_lower_val = curr_range['lower value']
			j = i + 1
			for j in range(j, len(ranges)):
				temp_range = ranges[j]
				temp_lower_val = temp_range['lower value']
				if temp_lower_val < curr_lower_val:
					ranges[i] = temp_range
					ranges[j] = curr_range

		number_line_string = '__'
		for temp_range_dict in ranges:
			temp_lower_val = str(temp_range_dict['lower value'])
			temp_includes_lower_val = temp_range_dict['includes lower value']
			temp_upper_val = str(temp_range_dict['upper value'])
			temp_includes_upper_val = temp_range_dict['includes upper value']
			if temp_includes_lower_val:
				temp_lower_limit_splitter = '['
			else:
				temp_lower_limit_splitter = '('
			if temp_includes_upper_val:
				temp_upper_limit_splitter = ']'
			else:
				temp_upper_limit_splitter = ')'
			temp_range_string = temp_lower_limit_splitter + temp_lower_val + ',' + temp_upper_val + temp_upper_limit_splitter + '__'
			number_line_string = number_line_string + temp_range_string
			
		print(number_line_string)

	def contains_range_exactly(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		range_dict = {
			'lower value': lower_val, 
			'upper value': upper_val,
			'includes lower value': includes_lower_val,
			'includes upper value': includes_upper_val
		}
		contains_range_exactly = False
		ranges = self.__ranges
		for temp_range_dict in ranges:
			if temp_range_dict == range_dict:
				contains_range_exactly = True

		return contains_range_exactly

	def contains_range_totally(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		is_valid_range = self.is_valid_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
		if is_valid_range:
			contains_range_totally = False
			ranges = self.__ranges
			for temp_range_dict in ranges:
				temp_lower_val = temp_range_dict['lower value']
				temp_includes_lower_val = temp_range_dict['includes lower value']
				temp_upper_val = temp_range_dict['upper value']
				temp_includes_upper_val = temp_range_dict['includes upper value']
				if temp_lower_val < lower_val and temp_upper_val > upper_val:
					contains_range_totally = True
				elif temp_lower_val == lower_val and temp_upper_val > upper_val:
					if temp_includes_lower_val or not temp_includes_lower_val and not includes_lower_val:
						contains_range_totally = True
				elif temp_lower_val < lower_val and temp_upper_val == upper_val:
					if temp_includes_upper_val or not temp_includes_upper_val and not includes_upper_val:
						contains_range_totally = True
				elif temp_lower_val == lower_val and temp_upper_val == upper_val:
					contains_lower_end = False
					contains_upper_end = False
					if temp_includes_lower_val or not temp_includes_lower_val and not includes_lower_val:
						contains_lower_end = True
					if temp_includes_upper_val or not temp_includes_upper_val and not includes_upper_val:
						contains_upper_end = True
					if contains_lower_end and contains_upper_end:
						contains_range_totally = True

		return contains_range_totally

	def contains_range_partially(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		is_valid_range = self.is_valid_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
		if is_valid_range:
			ranges = self.__ranges
		
			contains_range_partially = False
			for temp_range_dict in ranges:
				temp_lower_val = temp_range_dict['lower value']
				temp_includes_lower_val = temp_range_dict['includes lower value']
				temp_upper_val = temp_range_dict['upper value']
				temp_includes_upper_val = temp_range_dict['includes upper value']

				if lower_val >= temp_upper_val:
					if lower_val == temp_upper_val:
						if includes_lower_val or temp_includes_upper_val:
							contains_range_partially = True		
				elif upper_val <= temp_lower_val:
					if upper_val == temp_lower_val:
						if includes_upper_val or temp_includes_lower_val:
							contains_range_partially = True
				else:
					contains_range_partially = True
			
				if contains_range_partially:
					break
	
		return contains_range_partially

#----Range related helper methods----
	def is_valid_range(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		is_valid_range = False
		if lower_val == upper_val:
			if not includes_lower_val or not includes_upper_val:
				raise ValueError('includes_lower_val and includes_upper_val parameters must both be true when adding a single value')
		elif lower_val > upper_val:
			raise ValueError('upper_val parameter must be greater than or equal to lower_val paramter')
		if lower_val == upper_val and includes_lower_val and not includes_upper_val:
			raise ValueError('If upper_val parameter is equal to lower_val paramter they must both be included in the range')
		elif not isinstance(lower_val, numbers.Number):
			raise ValueError('lower_val parameter must be a numeric type (int, float, long, complex)')
		elif not isinstance(upper_val, numbers.Number):
			raise ValueError('upper_val parameter must be a numeric type (int, float, long, complex)')
		elif not isinstance(includes_lower_val, bool):
			raise ValueError('includes_lower_val parameter must be of type bool (boolean)')
		elif not isinstance(includes_lower_val, bool):
			raise ValueError('includes_upper_val parameter must be of type bool (boolean)')
		else:
			is_valid_range = True

		return is_valid_range

	def get_overlapping_ranges(self, lower_val, includes_lower_val, upper_val, includes_upper_val):
		is_valid_range = self.is_valid_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
		if is_valid_range:
			ranges = self.__ranges
	
			overlapping_ranges = []
			for temp_range_dict in ranges:
				temp_lower_val = temp_range_dict['lower value']
				temp_includes_lower_val = temp_range_dict['includes lower value']
				temp_upper_val = temp_range_dict['upper value']
				temp_includes_upper_val = temp_range_dict['includes upper value']

				contains_range_partially = False
				if lower_val >= temp_upper_val:
					if lower_val == temp_upper_val:
						if includes_lower_val or temp_includes_upper_val:
							contains_range_partially = True		
				elif upper_val <= temp_lower_val:
					if upper_val == temp_lower_val:
						if includes_upper_val or temp_includes_lower_val:
							contains_range_partially = True
				else:
					contains_range_partially = True
			
				if contains_range_partially:
					overlapping_ranges.append(temp_range_dict)
	
		return overlapping_ranges
	
	def merge_ranges(self, lower_val, includes_lower_val, upper_val, includes_upper_val, overlapping_ranges):
		is_valid_range = self.is_valid_range(lower_val, includes_lower_val, upper_val, includes_upper_val)
		if is_valid_range:
			new_lower_val = lower_val
			new_upper_val = upper_val
			new_includes_lower_val = includes_lower_val
			new_includes_upper_val = includes_upper_val
			for temp_range_dict in overlapping_ranges:
				temp_lower_val = temp_range_dict['lower value']
				temp_includes_lower_val = temp_range_dict['includes lower value']
				temp_upper_val = temp_range_dict['upper value']
				temp_includes_upper_val = temp_range_dict['includes upper value']
				if temp_lower_val < new_lower_val:
					new_lower_val = temp_lower_val
					new_includes_lower_val = temp_includes_lower_val
				elif temp_lower_val == new_lower_val and temp_includes_lower_val:
					new_includes_lower_val = True
				if temp_upper_val > new_upper_val:
					new_upper_val = temp_upper_val
					new_includes_upper_val = temp_includes_upper_val
				elif temp_upper_val == new_upper_val and temp_includes_upper_val:
					new_includes_upper_val = True
		
			merged_range_dict = {
				'lower value': new_lower_val, 
				'upper value': new_upper_val,
				'includes lower value': new_includes_lower_val,
				'includes upper value': new_includes_upper_val
			}

		return merged_range_dict
		
				
		
			
			
	


	

		
