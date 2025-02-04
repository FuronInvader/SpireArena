import enum
"""
	Power Enum for what type of thing sources an effect
"""
class SOURCE(enum.Enum):
	ATTACK = enum.auto()
	SKILL = enum.auto()
	POWER = enum.auto()
	FX = enum.auto()

class TRIGGER(enum.Enum):
	OFFENSE = enum.auto()
	DEFENSE = enum.auto()
	ON_DEATH = enum.auto()
		# Should have default that logs death and decrements friendly group's fight_on
	ON_KILL = enum.auto()
	ON_ATTACK = enum.auto()
	VS_ATTACK = enum.auto()
	ON_SKILL = enum.auto()
	VS_SKILL = enum.auto()
	ON_POWER_GAIN = enum.auto()
	VS_POWER_GAIN = enum.auto()
	ON_POWER_LOSE = enum.auto()
	VS_POWER_LOSE = enum.auto()
	ON_TURN = enum.auto()
	ON_PLAY = enum.auto()
	ON_HP_REDUCE = enum.auto()
	VS_HP_REDUCE = enum.auto()
	AFTER_ATTACK = enum.auto()
	AFTER_ATTACK_ED = enum.auto()

class DESCRIPTIONS():
	WEAK = "Reduce attack damage by 25%"
	SHACKLES = "Reduce Strength for 1 turn by 1 per stack"
	STRENGTH = "Increase damage by 1 per stack"
	VULNERABLE = "Increase attack damage by 50%"
	INTANGIBLE = "Reduce attack damage to 1"
	BLOCK = "Reduce attack damage by 1 per stack, then remove that many stacks"

"""
#0 PowerObject (Abstract)
	Defines an API for events in the fight:
		* Timing variants for ALL (BEFORE, ON, AFTER) : When to accept the event occurring
	Instanceable Examples of Enum classes
		* OffensePowers
			# Priority Order: Strength (3), Shackles (2), Weak (1)
		* DefensePowers
			# Priority Order: Vulnerable (3), Intangible (2), Block (use, 1)
		* UtilityPowers
			# On kill/death
				# FungiCombust
			# On/Vs attack/skill/power gain/power lose
				# Chosen Hex, Awoken Phase 1
			# On turn
				# Lagavulin, OrbWalker
			# On play
				# Giant Head, TimeEater
			# On/Vs hp reduce
				# Transient
			# After attack(ed)
				# Malleable, Thorns

	ATTRIBUTES:
		turns : Int (turns to live) or None (permanent)
		priority : Int (higher # == higher priority)
		triggers : List of POWER classes to activate on
	METHODS:
		Affect(value, cardtype, owner, target, *extra) : Implements the callback for the effect; returns value as it should be affected while applying side affects to owner and target
		Prepare(*extra) : Prepares the next Affect call (optional)
		TurnTick() : Reduce power lifespan each turn
"""
class Power():
	"""
		Shell of a class, holds a list of enum values for when it activates, a duration (None for infinite) and a method callback fitting the Affect API:
			self, value, cardtype, owner, target, *extra
		The callback method should affect value appropriately to achieve the power's end goals, and is provided access to the effect owner and effect target to apply any necessary side effects

		A second callback is bound to the Prepare API (not used for all powers):
			self, *extra
		This should use variables in *extra tuple to set object internal state in preparation for future calls to Affect()

		TurnTick should be called at the end of every turn on all powers for everything, decrements powers as needed. Returns True when the power should be eliminated
	"""
	def __init__(self, timings, priority, turns, callback, callback2=None, PrepareDescription=None, AffectDescription=None):
		if type(timings) is not list:
			try:
				timings = list(timings)
			except TypeError: # Just a single one
				timings = [timings]
		self.triggers = timings
		self.priority = priority
		self.turns = turns
		self.PrepareDescription = PrepareDescription
		self.AffectDescription = AffectDescription
		self.Affect = callback
		if callback2 is not None:
			# Override self.Prepare()
			self.Prepare = callback2
		self.name = self.Affect.__name__

	def __str__(self):
		turns_left = "infinity" if self.turns is None else str(self.turns)
		prepare = "" if self.PrepareDescription is None else f"Prepare: \"{self.PrepareDescription}\""
		affect = "" if self.AffectDescription is None else f"Affect: \"{self.AffectDescription}\""
		if prepare == "" and affect == "":
			definition = ""
		else:
			if prepare == "":
				definition = affect
			else:
				definition = prepare+", "+affect
			definition = ", "+definition
		return f"{self.name} [Priority {self.priority}, {turns_left} turns left{definition}]"

	def Prepare(self, *extra):
		# Shell method takes anything and does nothing
		pass

	def TurnTick(self):
		# Make Powers have a lifespan
		if self.turns is not None:
			self.turns -= 1
			return self.turns == 0
		else:
			return False

# Implement Powers as callbacks
# TRIGGER.OFFENSE
def WEAK(value, affectClass, source, target, *extra):
	"""
		Trigger should be TRIGGER.OFFENSE
		Priority should be 1
		Value = Outgoing Damage
		Reduce by 25% (round down)
		Side Effects: None
	"""
	return int(value * 0.75)
def SHACKLES(value, affectClass, source, target, *extra):
	"""
		TRIGGER should be TRIGGER.OFFENSE
		Priority should be 2
		Turns should be 1
		Value = Outgoing Damage
		Extra = ShackleAmount (use negative value for temporary strength but I don't think any monsters have that)
		Side Effects: None
	"""
	return max(0, value-extra[0])
def STRENGTH(value, affectClass, source, target, *extra):
	"""
		TRIGGER should be TRIGGER.OFFENSE
		Priority should be 3
		Turns should be None
		Value = Outgoing Damage
		Extra = StrengthAmount
		Side Effects: None
	"""
	return value+extra[0]
# TRIGGER.DEFENSE
def VULNERABLE(value, affectClass, source, target, *extra):
	"""
		TRIGGER should be TRIGGER.DEFENSE
		Priority should be 3
		Value = Outgoing Damage
		Increase by 50% (round down)
		Side Effects: None
	"""
	return int(value * 1.5)
def INTANGIBLE(value, affectClass, source, target, *extra):
	"""
		TRIGGER should be TRIGGER.DEFENSE
		Priority should be 2
		Value = Outgoing Damage
		Reduce to 1
		Side Effects: None
	"""
	return min(value, 1)
def BLOCK(value, affectClass, source, target, *extra):
	"""
		TRIGGER should be TRIGGER.DEFENSE
		Priority should be 2
		Turns should be None (This is not the BLOCK GAIN trigger, this is the BLOCK USE trigger -- it is ALWAYS ON)
		Value = Outgoing Damage
		Side Effects: Reduce BlockAmount in target by blocked amount
	"""
	available_block = target.Block
	blocked_damage = min(value, available_block)
	value -= blocked_damage
	target.Block = available_block - blocked_damage
	return value
