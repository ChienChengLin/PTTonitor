# -*- coding: utf-8 -*- 

from django.shortcuts import render
from django.http import HttpResponse


# data base
from id_query.models import UserWordFreq
from id_query.models import WordFreq
from id_query.models import UserFrequency
from id_query.models import IpBased
from id_query.models import TimeBased
from id_query.models import UserInteraction
from id_query.models import Post
from id_query.models import Comment
from id_query.models import Node
from id_query.models import Link
from id_query.models import Graph

import json
import csv
import os
import re
import sys
import codecs
import uniout
import itertools
import datetime
import time
import math
import telnetlib
import socket
from collections import defaultdict
# numpy
import numpy as np
import numpy.linalg as LA
# Multi-Threading
import threading
from Queue import Queue
# csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from gensim.models import word2vec
from gensim import models



def query(request):
    return render(request, "query.html")


@csrf_protect
@csrf_exempt
def link_info(request):
    if request.is_ajax():
        post_dict = {}
        comment_dict = {}
        source_posts = []
        temp_source_posts = []
        target_posts = []
        temp_target_posts = []

        source_id = request.POST['source']
        target_id = request.POST['target']

        ### find source user posts with target user comments
        source_posts_obj = Post.objects.filter(author = source_id)
        # post data is in database
        if(len(list(source_posts_obj)) > 0):
            for post in source_posts_obj:
                post_dict['title'] = post.title
                post_dict['date'] = post.date
                post_dict['url'] = post.url
                post_dict['comment'] = []

                target_comments_obj = post.comment_set.filter(user = target_id)
                # comment data is in database
                if(len(list(target_comments_obj)) > 0):
                    for comment in target_comments_obj:
                        comment_dict['content'] = comment.content
                        comment_dict['score'] = comment.score
                        post_dict['comment'].append(comment_dict)
                    
                    source_posts.append(post_dict)
                    post_dict = {}
                    comment_dict = {}                
                
                # comment data isn't in database
                else:
                    temp_source_posts.append(post_dict)
                    post_dict = {}
                    comment_dict = {} 



        # post data isn't in database
        else:
            pass

        source_posts = source_posts + temp_source_posts


        ### find target user posts with source user comments
        target_posts_obj = Post.objects.filter(author = target_id)
        # post data is in database
        if(len(list(target_posts_obj)) > 0):
            for post in target_posts_obj:
                post_dict['title'] = post.title
                post_dict['date'] = post.date
                post_dict['url'] = post.url
                post_dict['comment'] = []

                source_comments_obj = post.comment_set.filter(user = source_id)
                # comment data is in database
                if(len(list(source_comments_obj)) > 0):
                    for comment in source_comments_obj:
                        comment_dict['content'] = comment.content
                        comment_dict['score'] = comment.score
                        post_dict['comment'].append(comment_dict)

                    target_posts.append(post_dict)
                    post_dict = {}
                    comment_dict = {}

                # comment data isn't in database
                else:
                    temp_target_posts.append(post_dict)
                    post_dict = {}
                    comment_dict = {}


        # post data isn't in database
        else:
            pass

        target_posts = target_posts + temp_target_posts


    result_data = {}
    result_data[source_id] = source_posts
    result_data[target_id] = target_posts

    return HttpResponse(json.dumps(result_data))





id_tokens = defaultdict(list)
@csrf_protect
@csrf_exempt
def common_token(request):
    global model
    global id_tokens
    id_tokens.clear()

    # lock & Semaphore for Multi-Threading
    threadLimiter = threading.BoundedSemaphore(100)    
    lock = threading.Lock()


    if request.is_ajax():
        common_token = request.POST['token']
        query_id = request.POST['id']
        similar_words = [t[0] for t in model.most_similar(common_token, topn = 10)]
        similar_words.append(common_token)

        
        IP_obj = IpBased.objects.filter(user = query_id)
        # ip relation data is in database
        if(len(list(IP_obj)) > 0):
            friends = json.loads(IP_obj[0].friend)
        # ip relation data isn't in database
        else:
            friends = []
            friends.append(query_id)

        threads = []
        for friend in friends:
            threadLimiter.acquire()
            t = threading.Thread(target=token_comparison, args=(friend, similar_words, threadLimiter, lock))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


    print id_tokens
    return HttpResponse(json.dumps(id_tokens))


def token_comparison(friend, similar_words, threadLimiter, lock):
    global id_tokens

    FREQ_obj = UserWordFreq.objects.filter(user = friend)
    # freq obj exists in database and the freq content isn't empty
    if(len(list(FREQ_obj)) > 0 and len(FREQ_obj[0].wordfreq_set.all()) > 0):
        word_freq_objs = FREQ_obj[0].wordfreq_set.all()
        
        word_list = []
        for word_freq_obj in word_freq_objs:
            word_list.append(word_freq_obj.word)
        
        for similar_word in similar_words:                
            if(similar_word in word_list):
                lock.acquire()
                id_tokens[friend].append(similar_word)
                lock.release()
    else:
        pass

    '''
    FREQ_obj = UserFrequency.objects.filter(user = friend)
    # freq obj exists in database and the freq content isn't empty
    if(len(list(FREQ_obj)) > 0 and len(json.loads(FREQ_obj[0].freq).keys()) > 0):
        word_freq = json.loads(FREQ_obj[0].freq)
        
        for similar_word in similar_words:                
            if(similar_word in word_freq.keys()):
                lock.acquire()
                id_tokens[friend].append(similar_word)
                lock.release()
    else:
        pass
    '''
    
    threadLimiter.release()
    exit(1)


@csrf_protect
@csrf_exempt
def node_info(request):
    global node_id
    global id_info

    if request.is_ajax():
        ID = request.POST['id']
        print ID
        
        lock1.acquire()
        node_id = ID # invoke crawler
        
        FREQ_obj = UserWordFreq.objects.filter(user=ID)
        # freq obj exists in database and the freq content isn't empty
        if(len(list(FREQ_obj)) > 0 and len(FREQ_obj[0].wordfreq_set.all()) > 0):
            word_freq_objs = FREQ_obj[0].wordfreq_set.all()
            
            data = []
            for word_freq_obj in word_freq_objs:
                word = word_freq_obj.word
                freq = word_freq_obj.freq
                data.append([unicode(word).encode('utf-8'), freq, 1])
            

            f = open('./id_query/static/word_freq/word_freq.csv', "w")
            w = csv.writer(f)
            w.writerows(data)
            f.close()

        else:
            data = []
            data.append([unicode("none").encode('utf-8'), 1, 1]) 

            f = open('./id_query/static/word_freq/word_freq.csv', "w")
            w = csv.writer(f)
            w.writerows(data)
            f.close()

        '''
        FREQ_obj = UserFrequency.objects.filter(user = ID)

        # freq obj exists in database and the freq content isn't empty
        if(len(list(FREQ_obj)) > 0 and len(json.loads(FREQ_obj[0].freq).keys()) > 0):
            word_freq = json.loads(FREQ_obj[0].freq)
        
            length = len(word_freq.keys())
            if(length >= 50):
                top_word_freq = [t for t in sorted(word_freq.items(), key=lambda x: -x[1])][:50]
            else:
                top_word_freq = [t for t in sorted(word_freq.items(), key=lambda x: -x[1])][:length]

            data = []
            for word_freq in top_word_freq:
                word = word_freq[0]
                freq = word_freq[1]
                data.append([unicode(word).encode('utf-8'), freq, 1])

            f = open('./id_query/static/word_freq/word_freq.csv', "w")
            w = csv.writer(f)
            w.writerows(data)
            f.close()

        else:
            data = []
            data.append([unicode("none").encode('utf-8'), 1, 1]) 

            f = open('./id_query/static/word_freq/word_freq.csv', "w")
            w = csv.writer(f)
            w.writerows(data)
            f.close()
        '''


        while(node_id != ""):
            pass

        lock2.acquire()
        id_info_str = json.dumps(id_info)
        id_info = []
        lock2.release()

        lock1.release()
        return HttpResponse(id_info_str)



def show(request):
    start_time = datetime.datetime.now()
    
    global node_id
    global id_info

    Graph_threadLimiter = threading.BoundedSemaphore(300)    
    lock_for_nodes = threading.Lock()
    lock_for_links = threading.Lock()
    nodes_queue = Queue()
    links_queue = Queue()

    nodes = []
    links = []
    graph_dict = {}

    ID = str(request.GET.get('id')).encode('utf-8')
    
    lock1.acquire()
    node_id = ID # invoke crawler


    threads = []
    GRAPH_obj = Graph.objects.filter(user=ID)
    # graph obj exists in database
    if(len(list(GRAPH_obj)) > 0):
        NODE_objs = GRAPH_obj[0].node_set.all()
        for NODE_obj in NODE_objs:
            Graph_threadLimiter.acquire()
            t = threading.Thread(target=node_append, args=(NODE_obj, nodes_queue, lock_for_nodes, Graph_threadLimiter))
            t.start()
            threads.append(t)

        LINK_objs = GRAPH_obj[0].link_set.all()
        for LINK_obj in LINK_objs:
            Graph_threadLimiter.acquire()
            t = threading.Thread(target=link_append, args=(LINK_obj, links_queue, lock_for_links, Graph_threadLimiter))
            t.start()
            threads.append(t)
 
    # graph obj dosen't exist in database
    else:
        node_dict = {}

        node_dict['name'] = '?'
        node_dict['group'] = 1

        nodes.append(node_dict)
        node_dict = {}

    # wait for all threads finishing their job
    for t in threads:
        t.join()

    while(not nodes_queue.empty()):
        nodes.append(nodes_queue.get())
    while(not links_queue.empty()):
        links.append(links_queue.get())
    
    graph_dict['nodes'] = nodes
    graph_dict['links'] = links

    with open('./id_query/static/force_graph/graph.json', 'w') as fp:
        json.dump(graph_dict, fp, indent=2)

    FREQ_obj = UserWordFreq.objects.filter(user=ID)
    # freq obj exists in database and the freq content isn't empty
    if(len(list(FREQ_obj)) > 0 and len(FREQ_obj[0].wordfreq_set.all()) > 0):
        word_freq_objs = FREQ_obj[0].wordfreq_set.all()
        
        data = []
        for word_freq_obj in word_freq_objs:
            word = word_freq_obj.word
            freq = word_freq_obj.freq
            data.append([unicode(word).encode('utf-8'), freq, 1])
        

        f = open('./id_query/static/word_freq/word_freq.csv', "w")
        w = csv.writer(f)
        w.writerows(data)
        f.close()

    else:
        data = []
        data.append([unicode("none").encode('utf-8'), 1, 1]) 

        f = open('./id_query/static/word_freq/word_freq.csv', "w")
        w = csv.writer(f)
        w.writerows(data)
        f.close()

    '''
    FREQ_obj = UserFrequency.objects.filter(user = ID) 
    # freq obj exists in database and the freq content isn't empty
    if(len(list(FREQ_obj)) > 0 and len(json.loads(FREQ_obj[0].freq).keys()) > 0):
        word_freq = json.loads(FREQ_obj[0].freq)
    
        length = len(word_freq.keys())
        if(length >= 50):
            top_word_freq = [t for t in sorted(word_freq.items(), key=lambda x: -x[1])][:50]
        else:
            top_word_freq = [t for t in sorted(word_freq.items(), key=lambda x: -x[1])][:length]

        data = []
        for word_freq in top_word_freq:
            word = word_freq[0]
            freq = word_freq[1]
            data.append([unicode(word).encode('utf-8'), freq, 1])
        

        f = open('./id_query/static/word_freq/word_freq.csv', "w")
        w = csv.writer(f)
        w.writerows(data)
        f.close()

    else:
        data = []
        data.append([unicode("none").encode('utf-8'), 1, 1]) 

        f = open('./id_query/static/word_freq/word_freq.csv', "w")
        w = csv.writer(f)
        w.writerows(data)
        f.close()
    '''


    while(node_id != ""):
        pass

    lock2.acquire()
    id_info_render = id_info
    id_info = []
    lock2.release()

    lock1.release()

    elapsed_time = datetime.datetime.now() - start_time
    print "Query response time: " + str(elapsed_time)

    return render(request, "show.html", {'ID': ID, 'info0': id_info_render[0], 'info1': id_info_render[1], 'info2': id_info_render[2], 'info3': id_info_render[3], 'info4': id_info_render[4], 'info5': id_info_render[5]})


def node_append(NODE_obj, nodes_queue, lock_for_nodes, Graph_threadLimiter):
    node_dict = {}

    node_dict['name'] = NODE_obj.name
    node_dict['group'] = 1

    lock_for_nodes.acquire()
    nodes_queue.put(node_dict)
    lock_for_nodes.release()

    Graph_threadLimiter.release()

def link_append(LINK_obj, links_queue, lock_for_links, Graph_threadLimiter):
    link_dict = {}

    link_dict['source'] = LINK_obj.source
    link_dict['target'] = LINK_obj.target
    link_dict['total_comment'] = LINK_obj.total_comment
    link_dict['fan_comment'] = LINK_obj.fan_comment
    link_dict['comment_rate'] = LINK_obj.comment_rate
    link_dict['width'] = LINK_obj.width
    link_dict['value'] = LINK_obj.value

    lock_for_links.acquire()
    links_queue.put(link_dict)
    lock_for_links.release()

    Graph_threadLimiter.release()

def show_old(request):
    start_time = datetime.datetime.now()
    
    global node_id
    global id_info

    # lock & queue for Multi-Threading
    threadLimiter = threading.BoundedSemaphore(100)    
    lock = threading.Lock()
    queue = Queue()

    nodes = []
    links = []

    node_dict = {}
    graph_dict = {}
    node_index_dict = {}
    id_freq_dict = {}
    id_interaction_dict = {}

    ID = str(request.GET.get('id')).encode('utf-8')
    
    lock1.acquire()
    node_id = ID # invoke crawler

    IP_obj = IpBased.objects.filter(user = ID)
    TIME_obj = TimeBased.objects.filter(user = ID)
    # ip/time relation data is in database
    if(len(list(IP_obj)) > 0 and len(list(TIME_obj)) > 0):
        friends = json.loads(IP_obj[0].friend)
        friends2 = json.loads(TIME_obj[0].friend)
    # ip/time relation data isn't in database
    else:
        friends = []
        friends2 = [] 
        friends.append(ID)
        friends2.append(ID)


    FREQ_obj = UserFrequency.objects.filter(user = ID) 
    # freq obj exists in database and the freq content isn't empty
    if(len(list(FREQ_obj)) > 0 and len(json.loads(FREQ_obj[0].freq).keys()) > 0):
        word_freq = json.loads(FREQ_obj[0].freq)
    
        length = len(word_freq.keys())
        if(length >= 50):
            top_word_freq = [t for t in sorted(word_freq.items(), key=lambda x: -x[1])][:50]
        else:
            top_word_freq = [t for t in sorted(word_freq.items(), key=lambda x: -x[1])][:length]

        data = []
        for word_freq in top_word_freq:
            word = word_freq[0]
            freq = word_freq[1]
            data.append([unicode(word).encode('utf-8'), freq, 1])
        

        f = open('./id_query/static/word_freq/word_freq.csv', "w")
        w = csv.writer(f)
        w.writerows(data)
        f.close()

    else:
        data = []
        data.append([unicode("none").encode('utf-8'), 1, 1]) 

        f = open('./id_query/static/word_freq/word_freq.csv', "w")
        w = csv.writer(f)
        w.writerows(data)
        f.close()


    # nodes appending
    index = 0
    for friend in friends:
        
        # id_freq_dict
        FREQ_obj = UserFrequency.objects.filter(user = friend)
        # freq data is in database
        if(len(list(FREQ_obj)) > 0):
            id_freq_dict[friend] = json.loads(FREQ_obj[0].freq)
            node_dict['freq'] = FREQ_obj[0].freq
        # freq data isn't in database
        else:
            id_freq_dict[friend] = {}
            node_dict['freq'] = "{}"


        # id_interaction_dict
        INTERACTION_obj = UserInteraction.objects.filter(user = friend)
        # interaction data is in database
        if(len(list(INTERACTION_obj)) > 0):
            id_interaction_dict[friend] = json.loads(INTERACTION_obj[0].fans)
        # interaction data isn't in database
        else:
            id_interaction_dict[friend] = {}

        # node_index_dict
        node_dict['group'] = 1
        node_dict['name'] = friend

        node_index_dict[friend] = index
        index += 1

        nodes.append(node_dict)
        node_dict = {}
    
    # links appending
    # ip relation: the number of group users >= 2
    if(len(friends) > 1):
        before_chunks = []
        for a, b in itertools.combinations(friends, 2):
            before_chunks.append([a, b])

        threads = []
        n = int(math.ceil(len(before_chunks) / 25.0)) # the number of threads is 25
        for i in xrange(0, len(before_chunks), n):
            after_chunks = before_chunks[i:i + n]

            threadLimiter.acquire()
            t = threading.Thread(target=link_append, args=(after_chunks, node_index_dict, id_freq_dict, id_interaction_dict, queue, lock, friends2, threadLimiter))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        while(not queue.empty()):
            links.append(queue.get())
    

    graph_dict['nodes'] = nodes
    graph_dict['links'] = links


    with open('./id_query/static/force_graph/graph.json', 'w') as fp:
        json.dump(graph_dict, fp, indent=2)


    while(node_id != ""):
        pass

    lock2.acquire()
    id_info_render = id_info
    id_info = []
    lock2.release()

    lock1.release()

    elapsed_time = datetime.datetime.now() - start_time
    print "Query response time: " + str(elapsed_time)

    return render(request, "show.html", {'ID': ID, 'info0': id_info_render[0], 'info1': id_info_render[1], 'info2': id_info_render[2], 'info3': id_info_render[3], 'info4': id_info_render[4], 'info5': id_info_render[5]})


# Threading function to append links
def link_append_old(friend_pairwise, node_index_dict, id_freq_dict, id_interaction_dict, queue, lock, friends2, threadLimiter):
    link_dict = {}
    
    for pairwise in friend_pairwise:
        # similarity
        if(pairwise[0] in id_freq_dict.keys() and pairwise[1] in id_freq_dict.keys()):
            freq_a = id_freq_dict[pairwise[0]]
            freq_b = id_freq_dict[pairwise[1]]

            wordFrequencyPair = [freq_a, freq_b]
            similarity = getDocSimilarity(wordFrequencyPair, 1)

            if(similarity == -1):
                similarity = 0

        else:
            similarity = 0


        # interaction
        interaction_info = []
        if(pairwise[0] in id_interaction_dict.keys()):
            if(pairwise[1] in id_interaction_dict[pairwise[0]].keys()):
                interaction_info.append(id_interaction_dict[pairwise[0]][pairwise[1]])

        if(pairwise[1] in id_interaction_dict.keys()):
            if(pairwise[0] in id_interaction_dict[pairwise[1]].keys()):
                interaction_info.append(id_interaction_dict[pairwise[1]][pairwise[0]])


        # time/ip relation
        if(pairwise[0] in friends2 and pairwise[1] in friends2):
            if(len(interaction_info) == 0):
                link_dict['source'] = node_index_dict[pairwise[0]]
                link_dict['target'] = node_index_dict[pairwise[1]]
                link_dict['value'] = 1
                link_dict['width'] = similarity
                link_dict['fan_comment'] = 0
                link_dict['total_comment'] = 0
                link_dict['comment_rate'] = 0
            
            elif(len(interaction_info) == 1):
                if(pairwise[0] in id_interaction_dict.keys()):
                    if(pairwise[1] in id_interaction_dict[pairwise[0]].keys()):
                        link_dict['source'] = node_index_dict[pairwise[1]]
                        link_dict['target'] = node_index_dict[pairwise[0]]
                        link_dict['value'] = 1
                        link_dict['width'] = similarity
                        link_dict['fan_comment'] = interaction_info[0][0]
                        link_dict['total_comment'] = interaction_info[0][1]
                        link_dict['comment_rate'] = interaction_info[0][2]                     

                if(pairwise[1] in id_interaction_dict.keys()):
                    if(pairwise[0] in id_interaction_dict[pairwise[1]].keys()):
                        link_dict['source'] = node_index_dict[pairwise[0]]
                        link_dict['target'] = node_index_dict[pairwise[1]]
                        link_dict['value'] = 1
                        link_dict['width'] = similarity
                        link_dict['fan_comment'] = interaction_info[0][0]
                        link_dict['total_comment'] = interaction_info[0][1]
                        link_dict['comment_rate'] = interaction_info[0][2]

            elif(len(interaction_info) == 2):
                link_dict['source'] = node_index_dict[pairwise[1]]
                link_dict['target'] = node_index_dict[pairwise[0]]
                link_dict['value'] = 1
                link_dict['width'] = similarity
                link_dict['fan_comment'] = interaction_info[0][0]
                link_dict['total_comment'] = interaction_info[0][1]
                link_dict['comment_rate'] = interaction_info[0][2]
                
                lock.acquire()
                queue.put(link_dict)
                lock.release()
                
                link_dict['source'] = node_index_dict[pairwise[0]]
                link_dict['target'] = node_index_dict[pairwise[1]]
                link_dict['value'] = 1
                link_dict['width'] = similarity
                link_dict['fan_comment'] = interaction_info[1][0]
                link_dict['total_comment'] = interaction_info[1][1]
                link_dict['comment_rate'] = interaction_info[1][2]


        # don't have time relation but similarity >= 0.1
        elif(similarity >= 0.1):
            if(len(interaction_info) == 0):
                link_dict['source'] = node_index_dict[pairwise[0]]
                link_dict['target'] = node_index_dict[pairwise[1]]
                link_dict['value'] = 0
                link_dict['width'] = similarity
                link_dict['fan_comment'] = 0
                link_dict['total_comment'] = 0
                link_dict['comment_rate'] = 0
            
            elif(len(interaction_info) == 1):
                if(pairwise[0] in id_interaction_dict.keys()):
                    if(pairwise[1] in id_interaction_dict[pairwise[0]].keys()):
                        link_dict['source'] = node_index_dict[pairwise[1]]
                        link_dict['target'] = node_index_dict[pairwise[0]]
                        link_dict['value'] = 0
                        link_dict['width'] = similarity
                        link_dict['fan_comment'] = interaction_info[0][0]
                        link_dict['total_comment'] = interaction_info[0][1]
                        link_dict['comment_rate'] = interaction_info[0][2]                     

                if(pairwise[1] in id_interaction_dict.keys()):
                    if(pairwise[0] in id_interaction_dict[pairwise[1]].keys()):
                        link_dict['source'] = node_index_dict[pairwise[0]]
                        link_dict['target'] = node_index_dict[pairwise[1]]
                        link_dict['value'] = 0
                        link_dict['width'] = similarity
                        link_dict['fan_comment'] = interaction_info[0][0]
                        link_dict['total_comment'] = interaction_info[0][1]
                        link_dict['comment_rate'] = interaction_info[0][2]

            elif(len(interaction_info) == 2):
                link_dict['source'] = node_index_dict[pairwise[1]]
                link_dict['target'] = node_index_dict[pairwise[0]]
                link_dict['value'] = 0
                link_dict['width'] = similarity
                link_dict['fan_comment'] = interaction_info[0][0]
                link_dict['total_comment'] = interaction_info[0][1]
                link_dict['comment_rate'] = interaction_info[0][2]

                lock.acquire()
                queue.put(link_dict)
                lock.release()

                link_dict['source'] = node_index_dict[pairwise[0]]
                link_dict['target'] = node_index_dict[pairwise[1]]
                link_dict['value'] = 0
                link_dict['width'] = similarity
                link_dict['fan_comment'] = interaction_info[1][0]
                link_dict['total_comment'] = interaction_info[1][1]
                link_dict['comment_rate'] = interaction_info[1][2]


        # don't have time relation and similarity <= 0.1
        else:
            if(len(interaction_info) == 1):
                if(pairwise[0] in id_interaction_dict.keys()):
                    if(pairwise[1] in id_interaction_dict[pairwise[0]].keys()):
                        link_dict['source'] = node_index_dict[pairwise[1]]
                        link_dict['target'] = node_index_dict[pairwise[0]]
                        link_dict['value'] = 0
                        link_dict['width'] = similarity
                        link_dict['fan_comment'] = interaction_info[0][0]
                        link_dict['total_comment'] = interaction_info[0][1]
                        link_dict['comment_rate'] = interaction_info[0][2]                     

                if(pairwise[1] in id_interaction_dict.keys()):
                    if(pairwise[0] in id_interaction_dict[pairwise[1]].keys()):
                        link_dict['source'] = node_index_dict[pairwise[0]]
                        link_dict['target'] = node_index_dict[pairwise[1]]
                        link_dict['value'] = 0
                        link_dict['width'] = similarity
                        link_dict['fan_comment'] = interaction_info[0][0]
                        link_dict['total_comment'] = interaction_info[0][1]
                        link_dict['comment_rate'] = interaction_info[0][2]

            elif(len(interaction_info) == 2):
                link_dict['source'] = node_index_dict[pairwise[1]]
                link_dict['target'] = node_index_dict[pairwise[0]]
                link_dict['value'] = 0
                link_dict['width'] = similarity
                link_dict['fan_comment'] = interaction_info[0][0]
                link_dict['total_comment'] = interaction_info[0][1]
                link_dict['comment_rate'] = interaction_info[0][2]

                lock.acquire()
                queue.put(link_dict)
                lock.release()

                link_dict['source'] = node_index_dict[pairwise[0]]
                link_dict['target'] = node_index_dict[pairwise[1]]
                link_dict['value'] = 0
                link_dict['width'] = similarity
                link_dict['fan_comment'] = interaction_info[1][0]
                link_dict['total_comment'] = interaction_info[1][1]
                link_dict['comment_rate'] = interaction_info[1][2]

            else:
                link_dict = {}
                continue            

        lock.acquire()
        queue.put(link_dict)
        lock.release()

        link_dict = {}

    threadLimiter.release()
    exit(1)



# find the distance of two vectors
def getDocDistance(a, b):
    if LA.norm(a)==0 or LA.norm(b)==0:
        return -1

    return round(np.inner(a, b) / (LA.norm(a) * LA.norm(b)), 4)
    

# find similarity of two posts    
def getDocSimilarity(wordFrequencyPair, minTimes=1):
    dict1 = {}
    for key in wordFrequencyPair[0].keys():
        if wordFrequencyPair[0].get(key, 0) >= minTimes: # get value by key
            dict1[key] = wordFrequencyPair[0].get(key, 0) # store (key, value)

    dict2 = {}
    for key in wordFrequencyPair[1].keys():
        if wordFrequencyPair[1].get(key, 0) >= minTimes: # get value by key
            dict2[key] = wordFrequencyPair[1].get(key, 0) # store (key, value)

    for key in dict2.keys():
        if dict1.get(key, 0) == 0:
            dict1[key] = 0
        
    for key in dict1.keys():
        if dict2.get(key, 0) == 0:
            dict2[key] = 0
        
    v1 = []
    for w in sorted(dict1.keys()):
        v1.append(dict1.get(w))
        #print "(1)", w, dict1.get(w)

    v2 = []    
    for w in sorted(dict2.keys()):
        v2.append(dict2.get(w))
        #print "(2)", w, dict2.get(w)

    result = getDocDistance(v1, v2)
    return result


def crawler(account, password):
    print "##### Crawler trys to connect ..."

    global node_id
    global id_info
    # the bbs ip
    SITE_IP = 'ptt.cc'

    while(True):
        try:
            tn = telnetlib.Telnet(SITE_IP, timeout=10)
            time.sleep(1)

            # read content
            content = tn.read_very_eager().decode('big5', 'ignore')
            content = content.encode('utf-8')

            # login
            if '請輸入代號' in content:
                # write account id
                tn.write((account + '\r').encode('big5'))
                time.sleep(1)
                content = tn.read_very_eager().decode('big5', 'ignore')

                # write password
                tn.write((password + '\r').encode('big5'))
                time.sleep(2)
                content = tn.read_very_eager().decode('big5', 'ignore')
                content = content.encode('utf-8')
                
                # check if password incorrect
                if '密碼不對' in content:
                    sys.exit()

                # check if exists a session
                if '您想刪除其他重複登入的連線嗎' in content:
                    tn.write('Y\r'.encode('big5'))
                    time.sleep(7)
                    content = tn.read_very_eager().decode('big5', 'ignore')
                    content = content.encode('utf-8')

                # handle 'press any key'
                while '任意鍵' in content:
                    tn.write('\r'.encode('big5'))
                    time.sleep(2)
                    content = tn.read_very_eager().decode('big5', 'ignore')
                    content = content.encode('utf-8')

                # delete incorrectly login message
                if '編輯器自動復原' in content:
                    tn.write(('Q\r').encode('big5'))
                    time.sleep(1)
                    content = tn.read_very_eager().decode('big5', 'ignore')
                    content = content.encode('utf-8')

                # delete incorrectly login message
                if '要刪除以上錯誤嘗試' in content:
                    tn.write(('Y\r\n').encode('big5'))
                    time.sleep(1)
                    content = tn.read_very_eager().decode('big5', 'ignore')
                    content = content.encode('utf-8')

            # go to (T)alk    
            tn.write(('T\r').encode('big5'))
            time.sleep(1)
            content = tn.read_very_eager().decode('big5', 'ignore')
            content = content.encode('utf-8')
            # go to (Q)uery
            tn.write(('Q\r').encode('big5'))
            time.sleep(1)
            content = tn.read_very_eager().decode('big5', 'ignore')
            content = content.encode('utf-8')

            print "##### Crawler connects successful."

            auto_disconnect_count = 0

            preventIDLE_start_time = datetime.datetime.now()
            while(True):
                if(node_id != ""):
                    preventIDLE_start_time = datetime.datetime.now()
                    lock2.acquire()

                    # auto disconnection per 100 querys
                    auto_disconnect_count += 1
                    if(auto_disconnect_count > 100):
                        # close telnet                
                        tn.close()
                        break                       

                    # write ID to the query block                  
                    tn.write((str(node_id)+'\r').encode('big5'))
                    start_time = datetime.datetime.now()
                    
                    while('《ＩＤ暱稱》' not in content and '【聊天說話】' not in content):
                        content = tn.read_very_eager().decode('big5', 'ignore')
                        content = content.encode('utf-8')
                        
                        elapsed_time = (datetime.datetime.now() - start_time).seconds
                        if(elapsed_time > 10):
                            raise socket.error

                    # leave query page and enter again
                    tn.write(('Q\r').encode('big5'))
                    time.sleep(1)

                    # get someone's information
                    if '《ＩＤ暱稱》' in content:
                        start_position = content.find("《ＩＤ暱稱》")
                        end_position = content.find(")") + 1
                        username = content[start_position: end_position]
                        id_info.append(username)

                        start_position = content.find("《登入次數》")
                        end_position = content.find(" (同天內只計一次)")
                        login_times = content[start_position: end_position].strip('     ')
                        ansi_escape = re.compile(r'\x1b[^m]*m')
                        login_times = ansi_escape.sub('', login_times)
                        id_info.append(login_times)

                        start_position = content.find("《有效文章》")
                        end_position = content.find(" (退:0)")
                        post_amount = content[start_position: end_position].strip('     ')
                        id_info.append(post_amount)

                        start_position = content.find("《目前動態》")
                        end_position = content.find("《私人信箱》")
                        current = content[start_position: end_position].strip('     ')
                        ansi_escape = re.compile(r'\x1b[^m]*m')
                        current = ansi_escape.sub('', current)
                        id_info.append(current)

                        start_position = content.find("《上次上站》")
                        end_position = content.find("《上次故鄉》")
                        last_login_time = content[start_position: end_position].strip('     ')
                        id_info.append(last_login_time)

                        start_position = content.find("《上次故鄉》")
                        end_position = content.find("《 五子棋 》")
                        last_login_ip = content[start_position: end_position].strip('\r\n')
                        id_info.append(last_login_ip)

                        node_id = ""
                        lock2.release()


                        start_time = datetime.datetime.now()
                        while('請輸入使用者代號:' not in content):
                            content = tn.read_very_eager().decode('big5', 'ignore')
                            content = content.encode('utf-8')

                            elapsed_time = (datetime.datetime.now() - start_time).seconds
                            if(elapsed_time > 10):
                                raise socket.error


                    # someone is disappear                       
                    elif '【聊天說話】' in content:
                        start_time = datetime.datetime.now()
                        while('請輸入使用者代號:' not in content):
                            content = tn.read_very_eager().decode('big5', 'ignore')
                            content = content.encode('utf-8')

                            elapsed_time = (datetime.datetime.now() - start_time).seconds
                            if(elapsed_time > 10):
                                raise socket.error

                        node_id = ""
                        lock2.release()

                    # wrong page        
                    else:
                        # close telnet
                        tn.close()
                        print "!!!!! wrong page."
                        
                        node_id = ""
                        lock2.release()
                        break

                
                # prevent crawler idling
                preventIDLE_end_time = datetime.datetime.now()
                if (preventIDLE_end_time - preventIDLE_start_time).seconds > 60:
                    preventIDLE_start_time = datetime.datetime.now()

                    print "##### Crawler preventIDLE is invoked."
                    tn.write(('\r\r').encode('big5'))
                    time.sleep(1)

                    while('請輸入使用者代號:' not in content):
                        content = tn.read_very_eager().decode('big5', 'ignore')
                        content = content.encode('utf-8')

                


        
        except socket.error:
            # close telnet
            tn.close()
            print "!!!!! socket error occurs."
            raise

        except:
            # close telnet
            tn.close()
            print "!!!!! error occurs."
            raise


# main program
########### id query cralwer ###########
node_id = ""
id_info = []
lock1 = threading.Lock()
lock2 = threading.Lock()

t1 = threading.Thread(target=crawler, args=("NCKUcsie5566", "2706865"))
t1.setDaemon(True)
t1.start()

########### word2vec model ###########
model = models.Word2Vec.load_word2vec_format('med250.model.bin', binary=True)



