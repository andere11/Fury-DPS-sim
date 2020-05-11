# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 16:21:24 2020

@author: Eric
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#wep_MH=[114,213,2.9]
wep_MH=[101,188,2.3]
wep_OH=[71,134,2.4]
#wep_OH=[80,150,2.7]
wep_2H=[223,372,3.7]
wep_skill=307
hit_char=7
crit_char=25
DW=1
WF=1
HOJ=1
AP_base=1219
armor=336


#talent builds
#cruel 5 5% crit
#unbriedled wrath 5 40% chance to gen 1 rage per auto
#imp battle 5 25% improved attackpower from BS
#enrage 5
#duel wield 5 25% higher offhand damage
#imp exe 2 10 rage to exe
#deathwish 1
#BT 1
#2 imp HS 13 rage
#tactical mastery 1 rage every 3 seconds
# deep wounds 60% of damage over 12 sec
#impale 2 2.2 cri multplier


def Weapon_damage_func(wep,AP):
    dps_mod=AP/14*wep[2]
    weapon_damage=[wep[0]+dps_mod,wep[1]+dps_mod,wep[2]]
    return weapon_damage

def Attack_table(wep_skill,hit_char,crit_char,DW):
    dodge=(5+(63*5-(wep_skill))*0.1)/100
    glancing_blow=40.0/100
    if wep_skill>=305:
        basemiss=5+(63*5-wep_skill)*0.1
    else:
        basemiss=5+(63*5-wep_skill)*0.2
    if DW==1:
        miss=(20+basemiss*0.8-hit_char)/100
    else:
        miss=basemiss/100
    crit=(crit_char-3-1.8)/100
    hit=(1-miss-dodge-glancing_blow-crit)
    if hit<0:
        hit=0
    attack_table=[miss,dodge,glancing_blow,crit,hit]
    attack_range=[miss,sum(attack_table[0:2]),sum(attack_table[0:3]),sum(attack_table[0:4]),1 ]
    return attack_table, attack_range

def Swing(attack_range,wep_skill,wep,AP,armor):
    roll=np.random.rand(1)
    roll_damage=np.random.rand(1)
    roll_glance=np.random.rand(1)
    weapon_damage=Weapon_damage_func(wep,AP)
    if 1.3-0.05*(63*5-wep_skill)<0.91:
        bottom_glance=1.3-0.05*(63*5-wep_skill)
    else:
        bottom_glance=0.91
    if 1.2-0.03*(63*5-wep_skill)<0.99:
        top_glance=1.2-0.03*(63*5-wep_skill)
    else:
        top_glance=0.99
    glance_slope=(top_glance-bottom_glance)
    if roll[0]<attack_range[0]:
        swing='miss'
        damage=0
    elif roll[0]>attack_range[0] and roll[0]<attack_range[1]:
        swing='dodge'
        damage=0
    elif roll[0]>attack_range[1] and roll[0]<attack_range[2]:
        swing='glance'
        damage=(glance_slope*roll_glance[0]+bottom_glance)*((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0])
    elif roll[0]>attack_range[2] and roll[0]<attack_range[3]:
        swing='crit'
        damage=((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0])*2.2
    elif roll[0]>attack_range[3] and roll[0]<attack_range[4]:
        swing='hit'
        damage=((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0])
    DR=armor/(armor+400+85*(60+4.5*(60-59)))
    damage=damage*(1-DR)
    return swing,damage

def Crusader_chance(wep):
    proc=1.66*wep[2]
    return proc

def Windfury(swing,attack_range,wep_skill,wep,AP,armor,deathwish,flurry_count,WF):
    if swing=='hit' or swing=='crit' or swing=='glance':
        roll=np.random.rand(1)
        if roll[0]<0.2 and WF==1:
            swings_WF,damage_WF=Swing(attack_range,wep_skill,wep,AP+315,armor)
            if deathwish==1:
                damage_WF=damage_WF*1.2
            rage=Rage_gen(damage_WF,swings_WF,wep,3.5)
            hit_type_WF.append(swings_WF)
            damages_WF.append(damage_WF)
            if swings_WF=='crit':
                flurry_count=3
            else:
                flurry_count=flurry_count
        else:
            damage_WF=0
            rage=0
            flurry_count=flurry_count
    else:
        damage_WF=0
        rage=0
        flurry_count=flurry_count
    return damage_WF,rage,flurry_count


def Hand_of_justice(attack_range,wep_skill,wep,AP,armor,f,deathwish,flurry_count,WF):
    roll=np.random.rand(1)
    if roll[0]<=0.02:
        swing_HOJ,damage_HOJ=Swing(attack_range,wep_skill,wep,AP,armor)
        if deathwish==1:
            damage_HOJ=damage_HOJ*1.2
        rage_HOJ=Rage_gen(damage_HOJ,swing_HOJ,wep,f)
        hit_type_HOJ.append(swing_HOJ)
        damages_HOJ.append(damage_HOJ)
        if swing_HOJ=='crit':
            flurry_count=3
        else:
            flurry_count=flurry_count
    else:
        damage_HOJ=0
        rage_HOJ=0
    if damage_HOJ>0:
        damage_HOJ_WF,rage_WF,flurry_count=Windfury(swing_HOJ,attack_range,wep_skill,wep,AP,armor,deathwish,flurry_count,WF)
    else:
        damage_HOJ_WF=0
        rage_WF=0
    damage_HOJ=damage_HOJ+damage_HOJ_WF
    rage=rage_HOJ+rage_WF
    return damage_HOJ,rage,flurry_count

def Crusader_proc(n,wep,crusader_proc_time):
    roll=np.random.rand(1)
    if roll[0]<=(Crusader_chance(wep)/100):
        crusader=1
        crusader_proc_time=n
    elif crusader_proc_time>0:
        crusader=1
        crusader_proc_time=crusader_proc_time
    else:
        crusader=0
        crusader_proc_time=0
    return crusader,crusader_proc_time

def Rage_gen(damage,swing,wep,f):
    roll=np.random.rand(1)
    if swing=='hit':
        rage=(15*damage)/(4*230.6)+wep[2]*f/2
        if roll[0]<0.4:
            rage=rage+1
    elif swing=='glance':
        rage=(15*damage)/(4*230.6)+wep[2]*f/2
        if roll[0]<0.4:
            rage=rage+1
    elif swing=='crit':
        rage=(15*damage)/(4*230.6)+wep[2]*f/2*2
        if roll[0]<0.4:
            rage=rage+1
    else:
        rage=0
    return rage

    

def Yellow_attack_table(wep_skill,hit_char,crit_char):
    dodge=(5+(63*5-(wep_skill))*0.1)/100
    if wep_skill>=305:
        basemiss=5+(63*5-wep_skill)*0.1
    else:
        basemiss=5+(63*5-wep_skill)*0.2
    if basemiss>hit_char:
        miss=(basemiss-hit_char)/100
    else:
        miss=0
    crit=(crit_char-3-1.8)/100
    hit=(1-miss-dodge-crit)
    if hit<0:
        hit=0
    attack_table=[miss,dodge,crit,hit]
    attack_range=[miss,sum(attack_table[0:2]),sum(attack_table[0:3]),1 ]
    return attack_table, attack_range

def Bloodthirst(AP,hit_table_yellow,armor):
    roll=np.random.rand(1)
    if roll[0]<hit_table_yellow[0]:
        swing='miss'
        damage=0
    elif roll[0]>hit_table_yellow[0] and roll[0]<hit_table_yellow[1]:
        swing='dodge'
        damage=0
    elif roll[0]>hit_table_yellow[1] and roll[0]<hit_table_yellow[2]:
        swing='crit'
        damage=AP*0.45*2.2
    elif roll[0]>hit_table_yellow[2] and roll[0]<hit_table_yellow[3]:
        swing='hit'
        damage=AP*0.45
    DR=armor/(armor+400+85*(60+4.5*(60-59)))
    damage=damage*(1-DR)
    return swing,damage

def Heroic_strike(hit_table_yellow,wep_skill,wep,AP,armor):
    roll=np.random.rand(1)
    roll_damage=np.random.rand(1)
    weapon_damage=Weapon_damage_func(wep,AP)
    if roll[0]<hit_table_yellow[0]:
        swing='miss'
        damage=0
    elif roll[0]>hit_table_yellow[0] and roll[0]<hit_table_yellow[1]:
        swing='dodge'
        damage=0
    elif roll[0]>hit_table_yellow[1] and roll[0]<hit_table_yellow[2]:
        swing='crit'
        damage=((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0]+138)*2.2
    elif roll[0]>hit_table_yellow[2] and roll[0]<hit_table_yellow[3]:
        swing='hit'
        damage=damage=((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0]+138)
    DR=armor/(armor+400+85*(60+4.5*(60-59)))
    damage=damage*(1-DR)
    return swing,damage

def Execute(total_rage,hit_table_yellow,armor):
    roll=np.random.rand(1)
    if roll[0]<hit_table_yellow[0]:
        swing='miss'
        damage=0
    elif roll[0]>hit_table_yellow[0] and roll[0]<hit_table_yellow[1]:
        swing='dodge'
        damage=0
    elif roll[0]>hit_table_yellow[1] and roll[0]<hit_table_yellow[2]:
        swing='crit'
        damage=600+15*(total_rage-10)*2.2
    elif roll[0]>hit_table_yellow[2] and roll[0]<hit_table_yellow[3]:
        swing='hit'
        damage=600+15*(total_rage-10)
    DR=armor/(armor+400+85*(60+4.5*(60-59)))
    damage=damage*(1-DR)
    return swing,damage

def Whirlwind(weapon_damage,AP,hit_table_yellow,armor):
    roll=np.random.rand(1)
    roll_damage=np.random.rand(1)
    weapon_damage=Weapon_damage_func(weapon_damage,AP)
    if roll[0]<hit_table_yellow[0]:
        swing='miss'
        damage=0
    elif roll[0]>hit_table_yellow[0] and roll[0]<hit_table_yellow[1]:
        swing='dodge'
        damage=0
    elif roll[0]>hit_table_yellow[1] and roll[0]<hit_table_yellow[2]:
        swing='crit'
        damage=((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0])*2.2
    elif roll[0]>hit_table_yellow[2] and roll[0]<hit_table_yellow[3]:
        swing='hit'
        damage=((weapon_damage[1]-weapon_damage[0])*roll_damage[0]+weapon_damage[0])
    DR=armor/(armor+400+85*(60+4.5*(60-59)))
    damage=damage*(1-DR)
    return swing,damage

AP_range=np.arange(800,2300,50)
crit_range=np.arange(0,15,1)
AP_AP,C_C=np.meshgrid(AP_range,crit_range)
DPS_scaling=np.zeros([len(AP_range),len(crit_range)])
for k in range(0,len(AP_range)):
    for l in range(0,len(crit_range)):
        hit_char=crit_range[l]
        AP_base=AP_range[k]
        #simulation
        DPS_sim=[]
        total_DPS_MH=[]
        total_DPS_OH=[]
        total_DPS_BT=[]
        total_DPS_WW=[]
        total_DPS_EXE=[]
        total_DPS_HS=[]
        for i in range(0,1000):    
            if DW==0:
                wep_MH=wep_2H
            attack,attack_range=Attack_table(wep_skill,hit_char,crit_char,DW)
            attack_y,attack_range_y=Yellow_attack_table(wep_skill,hit_char,crit_char)
            attack_OH_HS,attack_range_OH_HS=Attack_table(wep_skill,hit_char,crit_char,0)
            crusader_proc_MH=Crusader_chance(wep_MH)
            crusader_proc_OH=Crusader_chance(wep_OH)
            damages_BT=[]
            hit_type_BT=[]
            damages_WW=[]
            hit_type_WW=[]
            damages_MH=[]
            hit_type_MH=[]
            damages_OH=[]
            hit_type_OH=[]
            hit_type_WF=[]
            damages_WF=[]
            hit_type_EXE=[]
            damages_EXE=[]
            hit_type_HS=[]
            damages_HS=[]
            hit_type_HOJ=[]
            damages_HOJ=[]
            rage_inst=[]
            DPS=[]
            time_count=[]
            BT_CD=0
            WW_CD=0
            MH_CD=0
            OH_CD=0
            EXE_CD=0
            total_rage=0
            total_damage=[]
            flurry_count=0
            HS_Q=0
            deathwish=0
            crusader_MH=0
            crusader_OH=0
            crusader_MH_proc_time=0
            crusader_OH_proc_time=0
            AP_step=[]
            for n in range(0,1000):
                damage_MH=0
                damage_OH=0
                damage_BT=0
                damage_WW=0
                damage_EXE=0
                damage_HS=0
                damage_HS_WF=0
                damage_MH_WF=0
                damage_BT_WF=0
                damage_EXE_WF=0
                damage_WW_WF=0
                damage_HOJ=0
                damage_HOJ_WF=0
                if crusader_MH==1 and crusader_OH==1 and (n-crusader_MH_proc_time)<150 and (n-crusader_OH_proc_time)<150:
                    AP=AP_base+400
                elif crusader_MH==1 and (n-crusader_MH_proc_time)<150:
                    AP=AP_base+200
                elif crusader_OH==1 and (n-crusader_OH_proc_time)<150:
                    AP=AP_base+200
                else:
                    AP=AP_base
                AP_step.append(AP)
                if n>=700:
                    deathwish=1
                if flurry_count>0:
                    speed_MH=wep_MH[2]*0.7
                    speed_OH=wep_OH[2]*0.7
                else:
                    speed_MH=wep_MH[2]
                    speed_OH=wep_OH[2]   
                if (n-MH_CD)>speed_MH*10:
                    MH_CD=n            
                    if flurry_count>0:
                        flurry_count=flurry_count-1
                    if HS_Q==1 and total_rage>=13:
                        swings_HS,damage_HS=Heroic_strike(attack_range_y,wep_skill,wep_MH,AP,armor)
                        if deathwish==1:
                            damage_HS=damage_HS*1.2
                        if damage_HS>0:
                            crusader_MH,crusader_MH_proc_time=Crusader_proc(n,wep_MH,crusader_MH_proc_time)
                            damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                        else:
                            rage_HOJ=0
                        hit_type_HS.append(swings_HS)
                        damages_HS.append(damage_HS)
                        total_rage=total_rage-13
                        damage_HS_WF,rage,flurry_count=Windfury(swings_HS,attack_range,wep_skill,wep_MH,AP,armor,deathwish,flurry_count,WF)
                        total_rage=total_rage+rage+rage_HOJ
                        if swings_HS=='crit':
                            flurry_count=3
                        HS_Q=0
                    else:
                        swings_MH,damage_MH=Swing(attack_range,wep_skill,wep_MH,AP,armor)
                        if deathwish==1:
                            damage_MH=damage_MH*1.2
                        if damage_MH>0:
                            crusader_MH,crusader_MH_proc_time=Crusader_proc(n,wep_MH,crusader_MH_proc_time)
                            damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                        else:
                            rage_HOJ=0
                        rage=Rage_gen(damage_MH,swings_MH,wep_MH,3.5)
                        total_rage=total_rage+rage+rage_HOJ
                        hit_type_MH.append(swings_MH)
                        damages_MH.append(damage_MH)
                        damage_MH_WF,rage,flurry_count=Windfury(swings_MH,attack_range,wep_skill,wep_MH,AP,armor,deathwish,flurry_count,WF)
                        if swings_MH=='crit':
                            flurry_count=3
                        HS_Q=0
                    if total_rage>=30 and (n-BT_CD)>25:
                        HS_Q=1
                if (n-OH_CD)>speed_OH*10 and DW==1:
                    OH_CD=n
                    if flurry_count>0:
                        flurry_count=flurry_count-1
                    if HS_Q==1:
                        swings_OH,damage_OH=Swing(attack_range_OH_HS,wep_skill,wep_OH,AP,armor)
                        if deathwish==1:
                            damage_OH=damage_OH*1.2
                        if damage_OH>0:
                            crusader_OH,crusader_OH_proc_time=Crusader_proc(n,wep_OH,crusader_OH_proc_time)
                            damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                        else:
                            rage_HOJ=0
                        rage=Rage_gen(damage_OH*0.75,swings_OH,wep_OH,1.75)
                        total_rage=total_rage+rage+rage_HOJ
                        hit_type_OH.append(swings_OH)
                        damages_OH.append(damage_OH*0.625)
                    else:
                        swings_OH,damage_OH=Swing(attack_range,wep_skill,wep_OH,AP,armor)
                        rage=Rage_gen(damage_OH*0.75,swings_OH,wep_OH,1.75)
                        if deathwish==1:
                            damage_OH=damage_OH*1.2
                        if damage_OH>0:
                            crusader_OH,crusader_OH_proc_time=Crusader_proc(n,wep_OH,crusader_OH_proc_time)
                            damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                        else:
                            rage_HOJ=0
                        total_rage=total_rage+rage+rage_HOJ
                        hit_type_OH.append(swings_OH)
                        damages_OH.append(damage_OH*0.625)
                    if swings_OH=='crit':
                        flurry_count=3
                if n>=880 and total_rage>=10 and (n-EXE_CD)>15:
                    EXE_CD=n
                    swings_EXE,damage_EXE=Execute(total_rage, attack_range_y, armor)
                    if deathwish==1:
                        damage_EXE=damage_EXE*1.2
                    hit_type_EXE.append(swings_EXE)
                    damages_EXE.append(damage_EXE)
                    if damage_EXE>0:
                        crusader_MH,crusader_MH_proc_time=Crusader_proc(n,wep_MH,crusader_MH_proc_time)
                        damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                    else:
                        rage_HOJ=0
                    if swings_EXE=='hit' or swings_EXE=='crit':
                        total_rage=0
                        damage_EXE_WF,rage,flurry_count=Windfury(swings_EXE,attack_range,wep_skill,wep_MH,AP,armor,deathwish,flurry_count,WF)
                        if damage_EXE_WF>0:
                            MH_CD=n
                        total_rage=total_rage+rage+rage_HOJ
                        if swings_EXE=='crit':
                            flurry_count=3
                    else:
                        total_rage=total_rage-5
                if (n-BT_CD)>60 and total_rage>=30 and n<=880:
                    BT_CD=n 
                    swings_BT,damage_BT=Bloodthirst(AP,attack_range_y,armor)
                    if deathwish==1:
                        damage_BT=damage_BT*1.2
                    if damage_BT>0:
                        crusader_MH,crusader_MH_proc_time=Crusader_proc(n,wep_MH,crusader_MH_proc_time)
                        damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                    else:
                        rage_HOJ=0
                    hit_type_BT.append(swings_BT)
                    damages_BT.append(damage_BT)
                    if swings_BT=='hit' or swings_BT=='crit':
                        total_rage=total_rage-30
                        damage_BT_WF,rage,flurry_count=Windfury(swings_BT,attack_range,wep_skill,wep_MH,AP,armor,deathwish,flurry_count,WF)
                        if damage_BT_WF>0:
                            MH_CD=n
                        total_rage=total_rage+rage+rage_HOJ
                    else:
                        total_rage=total_rage-5
                    if swings_BT=='crit':
                        flurry_count=3
                    
                if (n-WW_CD)>120 and total_rage>=50 and n<=880:
                    WW_CD=n
                    swings_WW,damage_WW=Whirlwind(wep_MH,AP,attack_range_y,armor)
                    if damage_WW>0:
                        crusader_MH,crusader_MH_proc_time=Crusader_proc(n,wep_MH,crusader_MH_proc_time)
                        damage_HOJ,rage_HOJ,flurry_count=Hand_of_justice(attack_range,wep_skill,wep_MH,AP,armor,3.5,deathwish,flurry_count,WF)
                    else:
                        rage_HOJ=0
                    if deathwish==1:
                        damage_WW=damage_WW*1.2
                    total_rage=total_rage-25+rage_HOJ
                    hit_type_WW.append(swings_WW)
                    damages_WW.append(damage_WW)
                    damage_WW_WF,rage,flurry_count=Windfury(swings_WW,attack_range,wep_skill,wep_MH,AP,armor,deathwish,flurry_count,WF)
                    if damage_WW_WF>0:
                        MH_CD=n
                    total_rage=total_rage+1
                    if swings_WW=='crit':
                        flurry_count=3
                if np.mod(n,30)==0:
                    total_rage=total_rage+1
                if total_rage>100:
                    total_rage=100
                rage_inst.append(total_rage)
                time_count.append(n)
                damage_WF=damage_MH_WF+damage_HS_WF+damage_BT_WF+damage_EXE_WF+damage_WW_WF+damage_HOJ_WF
                total_damage.append(damage_MH+damage_OH+damage_BT+damage_WW+damage_EXE+damage_HS+damage_WF+damage_HOJ)
            total_DPS_MH.append((np.sum(damages_MH)+np.sum(damages_WF)+np.sum(damages_HOJ))/100)
            total_DPS_OH.append(np.sum(damages_OH)/100)
            total_DPS_BT.append(np.sum(damages_BT)/100)
            total_DPS_WW.append(np.sum(damages_WW)/100)
            total_DPS_EXE.append(np.sum(damages_EXE)/100)
            total_DPS_HS.append(np.sum(damages_HS)/100)
        average_DPS_MH=np.average(total_DPS_MH)
        average_DPS_OH=np.average(total_DPS_OH)
        average_DPS_BT=np.average(total_DPS_BT)
        average_DPS_WW=np.average(total_DPS_WW)
        average_DPS_EXE=np.average(total_DPS_EXE)
        average_DPS_HS=np.average(total_DPS_HS)
        average_DPS=np.round(np.sum(average_DPS_MH+average_DPS_OH+average_DPS_BT+average_DPS_WW+average_DPS_EXE+average_DPS_HS))
        DPS_scaling[k,l]=average_DPS

#num_bins = 30
#n, bins, patches = plt.hist(DPS_sim, num_bins, facecolor='blue', alpha=0.5)
#plt.xlabel('DPS')
#plt.ylabel('Counts')
#plt.title('DB/crul: '+'$\mu='+str(sim_DPS_avg)+'$, $\sigma='+str(sim_std)+'$')
#plt.show()
#plt.figure()
#plt.plot(time_count,rage_inst)
#plt.xlabel('Time (s)')
#plt.ylabel('Rage')
#plt.figure()
#plt.plot(range(0,100),DPS)
#plt.xlabel('Time (s)')
#plt.ylabel('DPS')
