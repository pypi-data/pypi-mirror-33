def sai (theelist,grade=0):
	for jeer in theelist:
		if isinstance(jeer,list):
			sai(jeer,grade+1)
		else:
			for app in range(grade):
				print("\t",end='')
			print(jeer)