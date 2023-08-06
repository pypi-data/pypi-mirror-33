# Copyright 2018 Declan Hoare
# This file is part of Dipswitch.
#
# Dipswitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Dipswitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Dipswitch.  If not, see <http://www.gnu.org/licenses/>.
#
# __init__.py - implementation

class DuplicateCaseError(Exception):
	"""There is already a branch for the value."""
	pass

def switch(value):
	"""Generator for a switch statement."""
	options = {}
	i = 0
	jumped = False
	havedefault = False
	
	# The value of case to start with.  This stores information about
	# the possible branches in options, and always returns false, so
	# execution will always get to the end of the for loop and we can
	# change case next time.
	def fill(opt):
		if opt in options:
			raise DuplicateCaseError(f"There is already a branch for the value {opt}.")
		# len(options) is the same as how many times this function has
		# been called before.  The next iteration will call check in the
		# same order, so the number lets us index a branch.
		options[opt] = len(options)
		return False
	# Once the first iteration finishes, we know all of the options, so
	# now we find out which one, if any, equals value.
	
	# The check for value not being any of the options (in which case
	# we need to start at the default branch) is below.  This version
	# of check is yielded if the value is one of the options.
	def check_in(_):
		nonlocal i, jumped
		# If we've returned True once, we need to do so for every call
		# from now on, to allow fallthrough.  If the calling code has a
		# break, this the function won't get called anymore.
		if jumped:
			return True
		jumped = branch == i
		i += 1
		return jumped
	
	# This version of check is yielded if value isn't one of the
	# options.  branch is unset when this version is called, so it only
	# matters whether the default branch has been reached yet or not.
	def check_out(_):
		return jumped
	
	# This version of default is placed on fill.  Calling it more than
	# once means there's a duplicate case so we need to raise the
	# exception.
	def default_fill():
		nonlocal havedefault
		if havedefault:
			raise DuplicateCaseError("There is already a default branch.")
		havedefault = True
		return False
	
	# This version of default is placed on check_in.  We don't need to
	# start at the default branch, but fallthrough must still work.
	def default_in():
		return jumped
	
	# This version of default is placed on check_out.
	def default_out():
		nonlocal jumped
		jumped = True
		return True
	
	# We store default on the case function so that it can be accessed
	# without needing to mess with lame tuples and make this solution
	# even uglier.
	fill.default = default_fill
	check_in.default = default_in
	check_out.default = default_out
	
	# Start the first iteration.
	yield fill
	
	# options is filled in by the time control gets back here, so we
	# can check if the value is among them.
	try:
		branch = options[value]
	except KeyError:
		yield check_out
	else:
		yield check_in

