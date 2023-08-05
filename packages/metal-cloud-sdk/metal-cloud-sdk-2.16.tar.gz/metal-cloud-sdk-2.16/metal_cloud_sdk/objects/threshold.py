# -*- coding: utf-8 -*-

class Threshold(object):
	"""
	Threshold represents a certain property that if exceeded an infrastructure
	owner would be notified.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the Threshold
	"""
	threshold_id = None;

	"""
	The ID of the user
	"""
	user_id = None;

	"""
	The ID of the infrastructure
	"""
	infrastructure_id = None;

	"""
	The currency for the amount is the same as the pricing currency for the
	user's franchise
	"""
	threshold_cost = 0;

	"""
	The period of time that must pass before another warning is issued
	"""
	threshold_action_repeat_interval = "never";

	"""
	How is the threshold calculated
	"""
	threshold_type = "infrastructure_ondemand_and_metered_costs";

	"""
	What action to be taken when the threshold is exceeded
	"""
	threshold_action = "email";

	"""
	The schema type.
	"""
	type = None;
