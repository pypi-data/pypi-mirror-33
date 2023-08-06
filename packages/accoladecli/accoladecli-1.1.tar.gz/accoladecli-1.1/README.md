# accoladecli
A custom Command Line Interface for Accolade that provides our data partners access to our AWS servers. This should circumvent the necessity to use an sFTP as the middle man for transferring files. Requirements for this project are still to be decided. Items to keep in mind:
	1. File Naming:
		a. Must match what is happening currently with Influx- timestamp, date, company renaming, et2. Security:
	2. Identity authorization
		a.Token system is system for only data partners to access Accolade CLI
		b. All data being transferred must be encrypted- CLI should encrypt in transit
		c. Object-live login and Default encryption should be turned on within S3 bucket
		d. Give very limited access to what partners can and can’t do
			i. Only allowed push to their keys within a bucket and update
	3. Sending Bulk:
		a. Files should be able to be sent in bulk because timestamp matters
      		b. Each file currently has 5GB max due to AWS rules
	4. File Re-submitting:
		a. Resubmitted, updated files shouldn’t mess-up Workflow
		b. Proposed Idea:
			i. If Airflow not taken file out yet, simply updated(delete and replace)
			ii. If Airflow has take file out, place files into a Makeup folder that interacts with 					Workflow differently

