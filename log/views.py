from django.shortcuts import render,redirect, get_object_or_404
from .forms import ( ProfileForm, UserForm)

from django.utils import timezone
        
from .models import Profile, Tracks, Track_Coments  , Traj , history
from django.urls import reverse
from django.contrib.auth import authenticate, login,logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import PasswordChangeForm

import datetime
from datetime import time
import timeit

from django.conf import settings
import os
#from wordcloud import WordCloud
import random,string



import numpy as np

from django.db.models import Avg

from itertools import *
import json
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

#import tensorflow as tf
from neural_network import  history_update,display_songs

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
#from memory_profiler import profile



def custom_500(request):
    return render(request, '500.html', {}, status=500)

#@profile
def loggin(request):  
    logout(request)
 
    return render(request, 'login.html')    
#@profile    
def auth(request):
        error=False
        username=request.POST.get('username','')
        password=request.POST.get('password','')
        user=authenticate(username=username,password=password)
        
        if user is not None:
                if user.is_active:
                    login(request,user)
                    
                    
                    if Profile.objects.filter(user=request.user).exists():
                        prof = get_object_or_404(Profile, user=request.user)
                        #prof=Profile.objects.filter(user=request.user)
                   
                        if (prof.area=='' or prof.age=='' or prof.region=='' or prof.sex==''):
                            return redirect('profil')
                        else:
                            return redirect(reverse('homepage'))                       
                    else: 
                        #return render(request,'home.html',locals())
                        return redirect('profil')
        else:
            error=True
            return render(request,'login.html',{'error':error})

def loggout(request):
    
    logout(request)
    return redirect(reverse('login'))


#@profile
@login_required 
def homepage(request):
    """'affiche la liste des tracks'""" 
    tracks_list=list(np.load(os.path.join(settings.STATIC_ROOT, 'data/tracks_list.npy'))) 
    random.shuffle(tracks_list)

#    print tracks_list
   
    L=list(np.load(os.path.join(settings.STATIC_ROOT, 'data/L.npy')))
    for r in L:
        random.shuffle(r)
    
    if request.method=='GET':  
        
      
        if Profile.objects.filter(user=request.user).exists():
            prof = get_object_or_404(Profile, user=request.user)
            if (prof.area=='' or prof.age=='' or prof.region=='' or prof.sex==''):
                return redirect('profil')
            else:
              
                
                return render(request,'home.html',locals())
        else:     
            return redirect('profil')
    elif request.method=='POST' :
            if 'next_song' in request.POST:  
                
            ## start creating the trajectory  
                caracteres = string.ascii_letters + string.digits
                aleatoire = [random.choice(caracteres) for _ in range(6)]
                c=request.POST.get('next_song','')             
                t=Traj(path=['start']) 
                t.user=request.user
                t.key=''.join(aleatoire)
                t.save()          
                
                try:      
              
                    t3=Traj.objects.filter(user=request.user).order_by('-start_time')[1]  
                    
                    if (timezone.now()-t3.start_time).seconds >=900:
                    ## was the last conexion of the user more than 30min ago?
                        t2=history(path=['start'])
                        t2.user=request.user
                        t2.save()              
                except:
         
                    ## si pas de history
                    t2=history(path=['start']) 
                    t2.user=request.user
                   
                    t2.save()       
                    
                try:
          
                    t2=history.objects.filter(user=request.user).order_by('-start_time')[0]
                    
                except:
              
                    t2=history(path=['start']) 
                    t2.user=request.user               
                ## delimiteur 
                t2.append('XXX')
                t2.append_key(str(t.key))
          
                t2.save()
               
                return redirect(reverse('fiche_track',kwargs={'track_pseudo': c}))
            
            if 'profil' in request.POST:  
#                track_list = Tracks.objects.order_by('track_name')
                return render(request,'home.html',locals())

@login_required
def profil(request):  

    if request.method=='POST':       
        valid=True
        if 'age' in request.POST:
            if Profile.objects.filter(user=request.user).exists():   
                
                pp=Profile.objects.get(user=request.user)   
                pp.age=request.POST.get('age','')
                pp.region=request.POST.get('region','')
                pp.sex=request.POST.get('sex','')
                pp.area=request.POST.get('area','')
              
                pp.save()
                return render(request,'profil.html',locals())         
            else: 
                profil=ProfileForm
                form=profil(request.POST) 
                age=request.POST.get('age','')
                region=request.POST.get('region','')
                sex=request.POST.get('sex','')
                area=request.POST.get('area','')
                   
                pp=form.save(commit=False)
                pp.age=age
                pp.region=region
                pp.area=area    
                pp.sex=sex      
                pp.user=request.user
                pp.save() 
                return render(request,'profil.html',locals())        
    else:
        if Profile.objects.filter(user=request.user).exists():   
            pp=Profile.objects.get(user=request.user)  
        
        return render(request,'profil.html',locals())
               
def register(request):
    if request.method=='POST':
        #user_is_created=False
        form=UserForm(request.POST)
        #user_is_created=False
        
        if form.is_valid():
            user=form.save(commit=False)
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user.set_password(password)
            user.save()
            #user_is_created=True
            user=authenticate(username=username,password=password)
            login(request,user)
            return redirect('profil')  
        else:
            return render(request,'registration_form.html',{'form':form})
    else:
        form=UserForm(None)
        return render(request,'registration_form.html',{'form':form})
 



@csrf_exempt
def save_rating(request):
    if request.is_ajax():
        if request.method=='POST':
            rating=request.POST.get('rating')
            wordcloud=request.POST.get('wordcloud')
       
            track_pseudo=wcloud=request.POST.get('track_pseudo')
                
            track=get_object_or_404(Tracks, track_pseudo=track_pseudo)
            if not Track_Coments.objects.filter(user=request.user,track=track).exists():               
                t=Track_Coments(rating=rating)
                t.track=track
                t.user=request.user
                t.time=datetime.datetime.now()
                if wcloud!='':      
                    t.wordcloud=wordcloud

 
                    msg={'update_wcloud':True}
                  
                else:
                    msg={'update_wcloud':False}
                t.save()
                
                if Track_Coments.objects.filter(track=track).count()>=10:                        
                    track.track_popularity=Track_Coments.objects.filter(track=track).aggregate(Avg('rating'))['rating__avg']
                    track.save() 
                          
            
            return HttpResponse(json.dumps(msg),content_type="application/json")
    else:
        msg={'error':'No'}
        return HttpResponse(json.dumps(msg),content_type="application/json")
            
#@profile
def recommend_songs(request):
    
    novelty_parameters=5
    songs_by_type_features=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_by_type_features.npy')).item()
#    print songs_by_type_features['Country'].keys()
    if request.is_ajax():     
        if request.method=='GET':
            songs_db=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_db.npy')).item()


            t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]  
           
            length=len(t.path)
#            print t.path
#            print 'pathh'
#            print type(str(t.path[length-2]))
            if type(t.path[length-1])==unicode:               
                track_pseudo=t.path[length-1]
          
            elif type(t.path[length-1])==list:
                if len(t.path[length-1])<=2:
                    ### de la forme S(i-3) A(i-2) R(i-1)  donc le state est 
                    track_pseudo=t.path[length-3]
                else:
                    #### S A 
                    
                    track_pseudo=t.path[length-2]
                        
#            track=get_object_or_404(Tracks, track_pseudo=track_pseudo)
            track=songs_db[track_pseudo]
           
            
            t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
            historic=history_update(t2)  
            
            #### on update le novelty recovery pr la song qu on recommande
            genre=track['track_genre']
            index=songs_by_type_features[genre].keys().index(track_pseudo)
            if t2.novelty[genre  ][index][0]==novelty_parameters:                
               
                t2.novelty[genre ][ index ][0]=0.0    
#                print nov_recovery(t2.novelty[genre ][ songs_keys[track['track_genre']  ][track['track_pseudo'] ]][0])
            else:
                t2.novelty[genre][ index ][0]+=1.0 
            

                           
            model=settings.MODEL
            N=4
            epsilon=0.1
            l=display_songs(request.user,historic,track_pseudo,model,epsilon,N,t2)
            
#            w=predict_type(request.user,historic,track_pseudo,model)              
          
            
#            l=evaluate_actions(request.user,historic,track_pseudo,w,t2)
#            print l

            
#            l=['closer','closer','closer','closer']
            data={}
            for i in range(len(l)):
                song=songs_db[l[i]]
                index='#Eelement_'+str(i)             
                data[index]=song['Artist']+' - '+song['track_name']
                index='image_'+str(i)
                data[index]=song['Artist_image']
                index='#NOTE_'+str(i)
                data[index]=round(song['track_popularity'],2)
                index='.next_song_'+str(i)
                data[index]=song['track_pseudo']
                index='#genre_'+str(i)
                data[index]=song['track_genre']
#            print data


            if type(t.path[length-1])==unicode:  
#                    print 'ici'
                ### S           
                    t.path.append(l)
                #### S A 
                ##### OK
            elif type(t.path[length-1])==list:
                if t.path[length-2]==track_pseudo:
#                    print 'laa'
                    t.path[length-1]=l
            
            t.save()   
            
            #### update novelty pour tlm
            for s in t2.novelty:
                for p in range(len(t2.novelty[s])):
                    if t2.novelty[s][p][0]<novelty_parameters:                  
                        t2.novelty[s][p][0]+=1.0
            
            
            #### update songs qui sont montres pour eviter que ce soit toujours eux
            for rr in range(len(l)):
                song=songs_db[l[rr]]
                genre=song['track_genre']
                index=songs_by_type_features[genre].keys().index(l[rr])
                if t2.novelty[genre  ][index][0]==novelty_parameters:                              
                    t2.novelty[genre ][ index ][0]=2.0   
                else:
                    t2.novelty[genre][ index ][0]+=1.0 
                
                
             
            t2.save()

            return HttpResponse(json.dumps(data),content_type="application/json")
    else:
        data={'lol':False}
        return HttpResponse(json.dumps(data),content_type="application/json")
        
                        
    
@login_required       
def fiche_track(request, track_pseudo):
    novelty_parameters=5
    novelty_limit=60
    recommend_song=True
#    songs_keys=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_keys.npy')).item() 
    songs_by_type_features=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_by_type_features.npy')).item()
    
    songs_db=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_db.npy')).item() 
    track=songs_db[track_pseudo]
    TRack = get_object_or_404(Tracks, track_pseudo=track_pseudo)

    base_2=False
    has_yet_rated=True  
    path='wcloud_pictures/'+track_pseudo+'.png'
    


                
    try:
        REVIEW=Track_Coments.objects.get(user=request.user,track=TRack)        
    except:
        has_yet_rated=False             
        

    if request.method=='GET':      

        liste=[]
        N=4
        for i in range(N):
            liste.append('None')   

################################################################    
        t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]  
        length=len(t.path)
#        print t.path
        if t.path[length-1]=='start':
            t.path.append(track_pseudo)
          
            ### on obtient START  S
            ### OK
        if type(t.path[length-1])==list:
       
            ### S A R  ou  S A
            if len(t.path[length-1])<=2:
                ###  S A R
             
                t.path.append(track_pseudo)
                ### S A R S
            else:
#             len(t.path[length-1])>2:
                ### S A
                if t.path[length-2]!=track_pseudo:
#                    print 'il a actualiserrrr'
                    t.path.append([0.0,0.0])
                    t.path.append(track_pseudo)
                
                elif t.path[length-2]==track_pseudo:
                    print 'yes'
                    recommend_song=False
                    liste=[]
                    choix=t.path[length-1]
                    for i in choix:
                        liste.append(songs_db[str(i)])
                        
                 
                    
                    
        t.save()
                
    
                
        return render(request,'fiche_track.html',locals())
        
             
    elif request.method=='POST':
        if 'queue' in request.POST:
            
   
             #c=request.POST.get('next_song','') 
             titre_1=request.POST.get('titre_1','')
             titre_2=request.POST.get('titre_2','')
#             print titre_1
#             print titre_2
             t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]  
#             name=str(t.path[len(t.path)-2])
             
                  
             
#            ## collecting data        
             listening_time=request.POST.get('listening_time','') 
             if listening_time=='':
                listening_time=0  
             else:
                listening_time=round(float(listening_time),2)              
             percentage=request.POST.get('percentage','')
             if percentage=='':
                percentage=0
             else:
                percentage=round(float(percentage),2)           
             ## update the database 
             
#             liste=request.POST.get('liste2','')
#             t.path.append(liste)
             t.path.append([listening_time,percentage])
#           
             t.save()       
             #### history registering
             t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 


#             genre=get_object_or_404(Tracks, track_pseudo=track_pseudo).track_genre   

             genre=track['track_genre']
    
             # on inscrit le nom du track           
             
             length_t2=len(t2.path)
             
             if str(t2.path[length_t2-2][0])!=track_pseudo:     
                
                 t2.path.append([track_pseudo,genre])    
                 t2.path.append([listening_time,percentage])
                
             
#             for l in t2.novelty:
#                for p in range(len(t2.novelty[l])):
#                    if t2.novelty[l][p][0]<novelty_parameters:                  
#                        t2.novelty[l][p][0]+=1.0
#             
#             index=songs_by_type_features[ track['track_genre'] ].keys().index( track_pseudo )
#
#             if float(listening_time)>=novelty_limit:               
#                 if t2.novelty[genre][  index ][0]==novelty_parameters:                
#                     t2.novelty[genre ][   index  ][0]=0.0    
                    
                    
                        
                     
             t2.save()
             
             
             if str(titre_2)=='empty': 
#                 print 'laaaa'                                   
                 return redirect(reverse('fiche_track',kwargs={'track_pseudo': titre_1}))
             else:   
#                 print 'iiciii'
                 return redirect(reverse('solo',kwargs={'titre_1': titre_1,'titre_2':titre_2}))

## homepage
        elif 'liste' in request.POST:
            t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]
            #name=str(t.path[len(t.path)-2])
            listening_time=request.POST.get('listening_time2','')
            percentage=request.POST.get('percentage2','')
            
            if listening_time=='':
                listening_time=0
            else:
                listening_time=round(float(listening_time),2)
            if percentage=='':
                percentage=0
            else:
                percentage=round(float(percentage),2)
                       
            

            t.path.append([listening_time,percentage])
            
            t.path.append('end')
            t.save()
            
            #### history registering
            t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
            # on cherche le type de la musique
            
#            genre=get_object_or_404(Tracks, track_pseudo=track_pseudo).track_genre   
            
#            genre=str(Tracks.objects.filter(track_pseudo=name)[0].track_genre)

            genre=track['track_genre']
            # on inscrit le nom du track     
            
            length_t2=len(t2.path)
             
            if str(t2.path[length_t2-2][0])!=track_pseudo:     
                
                 t2.path.append([track_pseudo,genre])    
                 t2.path.append([listening_time,percentage])
                 
                 
#            for l in t2.novelty:
#                for p in range(len(t2.novelty[l])):
#                    if t2.novelty[l][p][0]<novelty_parameters:                  
#                        t2.novelty[l][p][0]+=1.0
#           
#            
#            
#            if float(listening_time)>=novelty_limit:
#                 
#                 if t2.novelty[track['track_genre']   ][ songs_keys[track['track_genre']   ][track['track_pseudo']   ]][0]==novelty_parameters:                
#                     t2.novelty[track['track_genre'] ][ songs_keys[track['track_genre']  ][track['track_pseudo']     ]][0]=0.0          
               
                     
            t2.save()
            return redirect(reverse('homepage'))
        
## logout        
        elif 'liste3' in request.POST:
            t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]
#            name=str(t.path[len(t.path)-2])
            listening_time=request.POST.get('listening_time2','')
            percentage=request.POST.get('percentage2','')
            
            if listening_time=='':
                listening_time=0
            else:
                listening_time=round(float(listening_time),2)
            if percentage=='':
                percentage=0
            else:
                percentage=round(float(percentage),2)
                       
            
            liste=request.POST.get('liste3','')
#            t.path.append(liste)
            t.path.append([listening_time,percentage])
            
            ## checker si end n est pqs deja mis
            ## voir si on keep track de la note de la zik aussi
            t.path.append('end')
            t.save()
            
            #### history registering
            t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
            # on cherche le type de la musique   
#            genre=str(Tracks.objects.filter(track_pseudo=name)[0].track_genre)
#            genre=get_object_or_404(Tracks, track_pseudo=track_pseudo).track_genre   
            genre=track['track_genre']
            # on inscrit le nom du track           
            
            
            
            length_t2=len(t2.path)
             
            if str(t2.path[length_t2-2][0])!=track_pseudo:     
                
                 t2.path.append([track_pseudo,genre])    
                 t2.path.append([listening_time,percentage])
                 
                 
            
#            for l in t2.novelty:
#                for p in range(len(t2.novelty[l])):
#                    if t2.novelty[l][p][0]<novelty_parameters:                  
#                        t2.novelty[l][p][0]+=1.0
#            if float(listening_time)>=novelty_limit:
##                 print np.array(t2.novelty[track.track_genre])
##                 print np.shape(np.array(t2.novelty[track.track_genre])
#                 
#                 if t2.novelty[track['track_genre']      ][songs_keys[track['track_genre']       ][track['track_pseudo']  ]][0]==novelty_parameters:                
#                     t2.novelty[track['track_genre']  ][songs_keys[track['track_genre'] ][track['track_pseudo'] ]][0]=0.0          
              
            t2.save()
            return redirect(reverse('logout'))
        
###############################################################
###############################################################         

        
@login_required         
def solo(request,titre_1,titre_2):
    novelty_parameters=2
    novelty_limit=60
    songs_by_type_features=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_by_type_features.npy')).item()
#    songs_keys=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_keys.npy')).item()  
    base_2=True
   
    songs_db=np.load(os.path.join(settings.STATIC_ROOT, 'data/songs_db.npy')).item()  
           
    track=songs_db[titre_1]
    TRack=get_object_or_404(Tracks, track_pseudo=titre_1)
    track2=songs_db[titre_2]
#    track2= get_object_or_404(Tracks, track_pseudo=titre_2)
    path='wcloud_pictures/'+titre_1+'.png'
    if Track_Coments.objects.filter(track=TRack,user=request.user).exists():
        has_yet_rated=True
#        review=Track_Coments.objects.filter(user=request.user,track=track)
#        REVIEW=Track_Coments.objects.get(user=request.user,track=TRack)
    else:
        has_yet_rated=False
#    print has_yet_rated
    
    if request.method=='GET':
        
        # check si existe pas deja
        t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]
        length=len(t.path)

        if t.path[length-5]!=titre_1 and t.path[length-2]!=titre_1:
            t.path.append(titre_1)
            t.path.append(['None','None',titre_2])
            
            
            
            
            #### on update le novelty recovery pr la song qu on recommande
            t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
            genre=track['track_genre']
            index=songs_by_type_features[genre].keys().index(titre_1)
            if t2.novelty[genre  ][index][0]==novelty_parameters:                             
                t2.novelty[genre ][ index ][0]=0.0    

            else:
                t2.novelty[genre][ index ][0]+=1.0 
            
            for l in t2.novelty:
                for p in range(len(t2.novelty[l])):
                    if t2.novelty[l][p][0]<novelty_parameters:                  
                        t2.novelty[l][p][0]+=1.0
                        
            t2.save()
        
        t.save()
        
                
        return render(request,'fiche_track2.html',locals())         
    else: ## methode=POST
        if 'solo' in request.POST:

             t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]   
             
#             name=str(t.path[len(t.path)-2])
#            ## collecting data        
             listening_time=request.POST.get('listening_time','') 
             if listening_time=='':
                listening_time=0  
             else:
                listening_time=round(float(listening_time),2)              
             percentage=request.POST.get('percentage','')
             if percentage=='':
                percentage=0
             else:
                percentage=round(float(percentage),2)           
             ## update the database
             
             #liste=request.POST.get('liste2','')
            
#             t.path.append(['None','None',titre_2])
             length=len(t.path)
             if t.path[length-5]!=titre_1:
                 t.path.append([listening_time,'option'])
#          
             t.save()
             t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
             # on cherche le type de la musique
             genre=get_object_or_404(Tracks, track_pseudo=track['track_pseudo']).track_genre   
        
             length_t2=len(t2.path)
             
             if str(t2.path[length_t2-2][0])!=track['track_pseudo']:     
                
                 t2.path.append([track['track_pseudo'],genre])    
                 t2.path.append([listening_time,percentage])
             
#             for l in t2.novelty:
#                for p in range(len(t2.novelty[l])):
#                    if t2.novelty[l][p][0]<novelty_parameters:                  
#                        t2.novelty[l][p][0]+=1.0
#             if float(listening_time)>=novelty_limit:
#               
#
#                 
#                 if t2.novelty[track ['track_genre']  ][songs_keys[track ['track_genre'] ][track['track_pseudo'] ]][0]==novelty_parameters:                
#                     t2.novelty[track ['track_genre']  ][songs_keys[track['track_genre']  ][track['track_pseudo'] ]][0]=0.0          
                
             t2.save()
             return redirect(reverse('fiche_track',kwargs={'track_pseudo': titre_2}))
# homepage

        elif 'home' in request.POST:
            t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]   
            
            name=str(t.path[len(t.path)-2])
            listening_time=request.POST.get('listening_time2','')
            percentage=request.POST.get('percentage2','')
            
            if listening_time=='':
                listening_time=0
            else:
                listening_time=round(float(listening_time),2)
            if percentage=='':
                percentage=0
            else:
                percentage=round(float(percentage),2)
                       
#            t.path.append(['None','None',titre_2])
            length=len(t.path)
            if t.path[length-5]!=titre_1:
                 t.path.append([listening_time,'option'])
            else:
                t.path.append([0.0,0.0])
            
            t.path.append('end')
            t.save()
            
            t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
            # on cherche le type de la musique
            
#            genre=str(Tracks.objects.filter(track_pseudo=name)[0].track_genre)
#            genre=get_object_or_404(Tracks, track_pseudo=name).track_genre   
            genre=songs_db[name]['track_genre']
            # on inscrit le nom du track           
      
            
            
            length_t2=len(t2.path)
             
            if str(t2.path[length_t2-2][0])!=name:     
                
                 t2.path.append([name,genre])    
                 t2.path.append([listening_time,percentage])
                 
                 
#            for l in t2.novelty:
#                for p in range(len(t2.novelty[l])):
#                    if t2.novelty[l][p][0]<novelty_parameters:                  
#                        t2.novelty[l][p][0]+=1.0
#                        
#            if float(listening_time)>=novelty_limit:
#                
#
#                 
#                 if t2.novelty[track['track_genre'] ][songs_keys[track['track_genre'] ][track['track_pseudo'] ]][0]==novelty_parameters:                
#                     t2.novelty[track['track_genre']  ][songs_keys[track['track_genre'] ][track['track_pseudo'] ]][0]=0.0          
                 
            t2.save()
            return redirect(reverse('homepage'))
# logout

        elif 'liste3' in request.POST:
            t=Traj.objects.filter(user=request.user).order_by('-start_time')[0]
            
            name=str(t.path[len(t.path)-2])
            
            listening_time=request.POST.get('listening_time2','')
            percentage=request.POST.get('percentage2','')
            
            if listening_time=='':
                listening_time=0
            else:
                listening_time=round(float(listening_time),2)
            if percentage=='':
                percentage=0
            else:
                percentage=round(float(percentage),2)
            
#            t.path.append(['None','None',titre_2])
            length=len(t.path)
            if t.path[length-5]!=titre_1:
                 t.path.append([listening_time,'option'])
            else:
                 t.path.append([0.0,0.0])
            ## checker si end n est pqs deja mis
            ## voir si on keep track de la note de la zik aussi
            t.path.append('end')
            t.save()
            
            t2=history.objects.filter(user=request.user).order_by('-start_time')[0] 
            # on cherche le type de la musique
            
#            genre=str(Tracks.objects.filter(track_pseudo=name)[0].track_genre)
#            genre=get_object_or_404(Tracks, track_pseudo=name).track_genre  
            genre=songs_db[name]['track_genre']
            # on inscrit le nom du track           
            
            
            length_t2=len(t2.path)
             
            if str(t2.path[length_t2-2][0])!=name:     
                
                 t2.path.append([name,genre])    
                 t2.path.append([listening_time,percentage])
                 
                 
#            for l in t2.novelty:
#                for p in range(len(t2.novelty[l])):
#                    if t2.novelty[l][p][0]<novelty_parameters:                  
#                        t2.novelty[l][p][0]+=1.0
#            if float(listening_time)>=novelty_limit:
#                
#
#                 
#                 if t2.novelty[track['track_genre'] ][songs_keys[track['track_genre'] ][track['track_pseudo'] ]][0]==novelty_parameters:                
#                     t2.novelty[track['track_genre']  ][songs_keys[track['track_genre'] ][track['track_pseudo'] ]][0]=0.0          
                 
            t2.save()
            return redirect(reverse('logout'))
              

def change_password(request):
    if request.method=='POST':
        form=PasswordChangeForm(data=request.POST,user=request.user)
        
        if form.is_valid():
            form.save()
            ### ca va deconnecter l user
            update_session_auth_hash(request, form.user)
            return render(request,'home.html')
        else:
            return redirect('change_password')
    else:
        form=PasswordChangeForm(user=request.user)
        return render(request,'change_password.html',locals())
   
    

##############################################################################
##############################################################################
##############################################################################
##############################################################################

    
