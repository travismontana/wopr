```
playDecisionTree:
	- condition: isplayAgentOrReveal
		Agent:
		-	condition: isHuman
			true:
			- question: "What card was played?"
			- question: "What action was taken?"
		  false:
			- question: "What card was drawn?"
			- question: "What action was taken?"
		Reveal:
		- condition: isHuman
			true:
			-	question: "What action was taken?"
			false:
			- question: "What action was taken?"

```