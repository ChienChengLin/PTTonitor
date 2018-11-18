from django.shortcuts import render
from django.http import HttpResponse

# csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

# time
import time
from datetime import date, datetime, timedelta
from time import mktime

# defaultdict
from collections import defaultdict

# database model
from keywords.models import TokenAmount
from keywords.models import MostUsedToken
from keywords.models import NegTokenScore
from keywords.models import CommentNegToken
from keywords.models import PosTokenScore
from keywords.models import CommentPosToken
from keywords.models import NegLegisScore
from keywords.models import NegLegisToken

# json
import json

# Multi-Threading
import threading
from Queue import Queue

# operator
import operator

# math
import math



# Create your views here.
def keywords(request):
    return render(request, "keywords.html")


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta


token_amount = defaultdict(int)
@csrf_protect
@csrf_exempt
def setDateInterval(request):
	global token_amount
	tokenRank = []
	token_dict = {}

    # lock & Semaphore for Multi-Threading
	threadLimiter = threading.BoundedSemaphore(15)    
	lock = threading.Lock()

	if request.is_ajax():
		print request.POST['startDate']
		print request.POST['endDate']

		# no need to retrieve data from database
		if(request.POST['startDate'] == '2016/06/18' and request.POST['endDate'] == '2016/11/17'):
			All_dates = 1
			return HttpResponse(All_dates)

		else:
			All_dates = 0

		startDate = time.strptime(request.POST['startDate'], "%Y/%m/%d")
		endDate = time.strptime(request.POST['endDate'], "%Y/%m/%d")	
    	
    	# transform into datetime format
		startDate_dtFormat = datetime.fromtimestamp(mktime(startDate))
		endDate_dtFormat = datetime.fromtimestamp(mktime(endDate))

		# generate date interval list
		dateInterval_list = []
		for result in perdelta(startDate_dtFormat, endDate_dtFormat, timedelta(days=1)):
			dateInterval_list.append(result.strftime("%Y/%m/%d"))


		threads = []
		# generate token_amount dict
		for per_date in dateInterval_list:
			threadLimiter.acquire()

			t = threading.Thread(target=addTokenAmount, args=(per_date, threadLimiter, lock))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		# generate tokenRank list
		for token, amount in token_amount.iteritems():
			token_dict['key'] = token
			token_dict['value'] = amount

			tokenRank.append(token_dict)
			token_dict = {}

		token_amount.clear()

		# dump tokenRank json file
		with open('./id_query/static/chart/MostUsedTokens_interval.json', 'w') as fp:
			json.dump(tokenRank, fp, indent=2)


	return HttpResponse(All_dates)


def addTokenAmount(per_date, threadLimiter, lock):
	global token_amount

	try:
		MostUsedToken_obj = MostUsedToken.objects.filter(date=per_date)[0]
		all_tokenAmount_objs = MostUsedToken_obj.tokenamount_set.all()
		for tokenAmount_obj in all_tokenAmount_objs:
			lock.acquire()
			token_amount[tokenAmount_obj.token] = token_amount[tokenAmount_obj.token] + tokenAmount_obj.amount
			lock.release()

		threadLimiter.release()
		exit(1)

	except IndexError:
		threadLimiter.release()
		exit(1)



token_score = defaultdict(float)
@csrf_protect
@csrf_exempt
def setDateInterval_CNT(request):
	global token_score
	tokenRank = []
	token_dict = {}

	# lock & Semaphore for Multi-Threading
	threadLimiter = threading.BoundedSemaphore(15)    
	lock = threading.Lock()

	if request.is_ajax():
		print request.POST['startDate']
		print request.POST['endDate']
		
		# no need to retrieve data from database
		if(request.POST['startDate'] == '2016/06/18' and request.POST['endDate'] == '2016/11/17'):
			All_dates = 1
			return HttpResponse(All_dates)

		else:
			All_dates = 0

		startDate = time.strptime(request.POST['startDate'], "%Y/%m/%d")
		endDate = time.strptime(request.POST['endDate'], "%Y/%m/%d")	
    	
		# transform into datetime format
		startDate_dtFormat = datetime.fromtimestamp(mktime(startDate))
		endDate_dtFormat = datetime.fromtimestamp(mktime(endDate))

		# generate date interval list
		dateInterval_list = []
		for result in perdelta(startDate_dtFormat, endDate_dtFormat, timedelta(days=1)):
			dateInterval_list.append(result.strftime("%Y/%m/%d"))

		threads = []
		# generate token_amount dict
		for per_date in dateInterval_list:
			threadLimiter.acquire()

			t = threading.Thread(target=addTokenScore_CNT, args=(per_date, threadLimiter, lock))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		OldMax = max(token_score.iteritems(), key=operator.itemgetter(1))[1]
		OldMin = min(token_score.iteritems(), key=operator.itemgetter(1))[1]
		NewMax = float(100)
		NewMin = float(0)
		OldRange = (OldMax - OldMin)  
		NewRange = (NewMax - NewMin)


		# generate tokenRank list
		for token, score in token_score.iteritems():
			token_dict['key'] = token
			NewValue = (((score - OldMin) * NewRange) / OldRange) + NewMin
			token_dict['value'] = math.ceil(NewValue)

			tokenRank.append(token_dict)
			token_dict = {}

		token_score.clear()

		# dump tokenRank json file
		with open('./id_query/static/chart/CommentNegTokens_interval.json', 'w') as fp:
			json.dump(tokenRank, fp, indent=2)


	return HttpResponse(All_dates)


def addTokenScore_CNT(per_date, threadLimiter, lock):
	global token_score

	try:
		CommentNegToken_obj = CommentNegToken.objects.filter(date=per_date)[0]
		all_tokenScore_objs = CommentNegToken_obj.negtokenscore_set.all()
		for tokenScore_obj in all_tokenScore_objs:
			lock.acquire()
			token_score[tokenScore_obj.token] = token_score[tokenScore_obj.token] + (tokenScore_obj.score * (-1))
			lock.release()

		threadLimiter.release()
		exit(1)

	except IndexError:
		threadLimiter.release()
		exit(1)



@csrf_protect
@csrf_exempt
def setDateInterval_CPT(request):
	global token_score
	tokenRank = []
	token_dict = {}

	# lock & Semaphore for Multi-Threading
	threadLimiter = threading.BoundedSemaphore(15)    
	lock = threading.Lock()

	if request.is_ajax():
		print request.POST['startDate']
		print request.POST['endDate']


		# no need to retrieve data from database
		if(request.POST['startDate'] == '2016/06/18' and request.POST['endDate'] == '2016/11/17'):
			All_dates = 1
			return HttpResponse(All_dates)

		else:
			All_dates = 0


		startDate = time.strptime(request.POST['startDate'], "%Y/%m/%d")
		endDate = time.strptime(request.POST['endDate'], "%Y/%m/%d")	
    	
		# transform into datetime format
		startDate_dtFormat = datetime.fromtimestamp(mktime(startDate))
		endDate_dtFormat = datetime.fromtimestamp(mktime(endDate))

		# generate date interval list
		dateInterval_list = []
		for result in perdelta(startDate_dtFormat, endDate_dtFormat, timedelta(days=1)):
			dateInterval_list.append(result.strftime("%Y/%m/%d"))

		threads = []
		# generate token_amount dict
		for per_date in dateInterval_list:
			threadLimiter.acquire()

			t = threading.Thread(target=addTokenScore_CPT, args=(per_date, threadLimiter, lock))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		OldMax = max(token_score.iteritems(), key=operator.itemgetter(1))[1]
		OldMin = min(token_score.iteritems(), key=operator.itemgetter(1))[1]
		NewMax = float(100)
		NewMin = float(0)
		OldRange = (OldMax - OldMin)  
		NewRange = (NewMax - NewMin)


		# generate tokenRank list
		for token, score in token_score.iteritems():
			token_dict['key'] = token
			NewValue = (((score - OldMin) * NewRange) / OldRange) + NewMin
			token_dict['value'] = math.ceil(NewValue)

			tokenRank.append(token_dict)
			token_dict = {}

		token_score.clear()

		# dump tokenRank json file
		with open('./id_query/static/chart/CommentPosTokens_interval.json', 'w') as fp:
			json.dump(tokenRank, fp, indent=2)


	return HttpResponse(All_dates)


def addTokenScore_CPT(per_date, threadLimiter, lock):
	global token_score

	try:
		CommentPosToken_obj = CommentPosToken.objects.filter(date=per_date)[0]
		all_tokenScore_objs = CommentPosToken_obj.postokenscore_set.all()
		for tokenScore_obj in all_tokenScore_objs:
			lock.acquire()
			token_score[tokenScore_obj.token] = token_score[tokenScore_obj.token] + tokenScore_obj.score
			lock.release()

		threadLimiter.release()
		exit(1)

	except IndexError:
		threadLimiter.release()
		exit(1)



@csrf_protect
@csrf_exempt
def setDateInterval_NLT(request):
	global token_score
	tokenRank = []
	token_dict = {}

	# lock & Semaphore for Multi-Threading
	threadLimiter = threading.BoundedSemaphore(15)    
	lock = threading.Lock()

	if request.is_ajax():
		print request.POST['startDate']
		print request.POST['endDate']
		
		# no need to retrieve data from database
		if(request.POST['startDate'] == '2016/06/18' and request.POST['endDate'] == '2016/11/17'):
			All_dates = 1
			return HttpResponse(All_dates)

		else:
			All_dates = 0


		startDate = time.strptime(request.POST['startDate'], "%Y/%m/%d")
		endDate = time.strptime(request.POST['endDate'], "%Y/%m/%d")	
    	
		# transform into datetime format
		startDate_dtFormat = datetime.fromtimestamp(mktime(startDate))
		endDate_dtFormat = datetime.fromtimestamp(mktime(endDate))

		# generate date interval list
		dateInterval_list = []
		for result in perdelta(startDate_dtFormat, endDate_dtFormat, timedelta(days=1)):
			dateInterval_list.append(result.strftime("%Y/%m/%d"))

		threads = []
		# generate token_amount dict
		for per_date in dateInterval_list:
			threadLimiter.acquire()

			t = threading.Thread(target=addTokenScore_NLT, args=(per_date, threadLimiter, lock))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		OldMax = max(token_score.iteritems(), key=operator.itemgetter(1))[1]
		OldMin = min(token_score.iteritems(), key=operator.itemgetter(1))[1]
		NewMax = float(100)
		NewMin = float(0)
		OldRange = (OldMax - OldMin)  
		NewRange = (NewMax - NewMin)


		# generate tokenRank list
		for token, score in token_score.iteritems():
			token_dict['key'] = token
			NewValue = (((score - OldMin) * NewRange) / OldRange) + NewMin
			
			if(math.ceil(NewValue) > 100):
				token_dict['value'] = 100
			else:
				token_dict['value'] = math.ceil(NewValue)

			tokenRank.append(token_dict)
			token_dict = {}

		token_score.clear()

		# dump tokenRank json file
		with open('./id_query/static/chart/NegLegisTokens_interval.json', 'w') as fp:
			json.dump(tokenRank, fp, indent=2)


	return HttpResponse(All_dates)


def addTokenScore_NLT(per_date, threadLimiter, lock):
	global token_score

	try:
		NegLegisToken_obj = NegLegisToken.objects.filter(date=per_date)[0]
		all_tokenScore_objs = NegLegisToken_obj.neglegisscore_set.all()
		for tokenScore_obj in all_tokenScore_objs:
			lock.acquire()
			token_score[tokenScore_obj.token] = token_score[tokenScore_obj.token] + (tokenScore_obj.score * (-1))
			lock.release()

		threadLimiter.release()
		exit(1)

	except IndexError:
		threadLimiter.release()
		exit(1)
