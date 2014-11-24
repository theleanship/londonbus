user = {
	'id': '',
	'username': '',
	'password': '',
	'alertPreferences': {
		'transport': 1, 	// 1=notifications, potentially email/text
		'periods': [
			{ 'start': '0730', 'end': '1000' }, 
			{ 'start': '1600', 'end': '1800' }
		]
	}
}

watch = {
	'user': 'userID',
	'type': '1',			// 1=tube, 2=line, 3=bus, 4=route
	'id': 'BNK'
}

disruption = {
	'type': 1, 				// 1=tube, 2=line, 3=bus, 4=route
	'id': 'BNK',
	'found': 000000000, 	// timestamp
	'removed': 00000000, 	// timestamp
	'source': 1,			// 1=API, 2=twitter, 3=user
	''
}