#!/usr/bin/python3


import textwrap
import sys
import json
import codecs
import re
import hashlib
from datetime import date
from pprint import pprint

hq=10
side='rebel'
version=1048
verbosity=0
planet='planet1'
xdate=date.today().isoformat()

elements=[]
cratedata={}
crateitemdata={}
cratescaledata={}
basedata={}
langdata={}
data={}
config={'table':[],'lang':'en-US','output':'list'}
config['targettranslation']={'HQ':'HQ', 'bruiserInfantry':'Heavy infantry', 'bruiserVehicle':'Heavy vehicle', 'building':'Other building', 'champion':'Droideka', 'flierInfantry':'Flying infantry', 'flierVehicle':'Flying vehicle', 'healerInfantry':'Support troop', 'heroBruiserInfantry':'Heavy infantry hero', 'heroBruiserVehicle':'Heavy vehicular hero', 'heroInfantry':'Infantry hero', 'heroVehicle':'Vehicle hero', 'infantry':'Infantry', 'resource':'Ressource generator', 'shield':'Shield', 'shieldGenerator':'Shield generator', 'storage':'Storage', 'trap':'Trap','turret':'Turret', 'vehicle':'Light vehicle', 'wall':'Wall'}
xhelp={}
morehelp={}
indexdata={}

def log(string):
    global config
    outputs=config['output'].split(",")
    if 'verbose' in outputs:
        print(string)

def importfile(filename):
    global config
    global data
    with open('content/{0}/patches/{1}.json'.format(config['version'],filename)) as swcfile:
        swcdata=json.load(swcfile)
        for table in swcdata['content']['objects']:
            if (not(table in data)):
                data[table]={}
            if (isinstance(swcdata['content']['objects'][table],list)):
                for item in swcdata['content']['objects'][table]:
                    if 'uid' in item:
                        uid=item['uid']
                        if (not(uid in data[table])):
                            data[table][uid]={}
                        for v in item:
                            data[table][uid][v]=item[v]
                    else:
                        print('Warning: item has no uid')
                        pprint(item)
                        sys.exit(0)
            
def importlangfile(lang):
    global config
    global langdata
    with codecs.open('content/{}/strings/strings_{}.json'.format(config['version'],lang),'r','utf-8') as stringsfile:
        langdict=json.load(stringsfile)
        for x in langdict['content']['objects']['LocalizedStrings']:
            if 'text' in x:
                langdata[x['uid']]=x['text']
    with codecs.open('content/{}/strings/strings-hn_{}.json'.format(config['version'],lang),'r','utf-8') as stringsfile:
        langdict=json.load(stringsfile)
        for x in langdict['content']['objects']['LocalizedStrings']:
            if 'text' in x:
                langdata[x['uid']]=x['text']

def setconfig(x,y):
    global config
    configitems={'hq':'HQ level','lang':'language','side':'faction'}
    for j in ['verbosity','version','planet','mode','output','begin','end','table']:
        configitems[j]=j
    intitems=['hq','verbosity','version']
    arrayitems=['table']
    alloweditems={'side':['empire','rebel','neutral','smuggler','tusken']}
    if x in configitems:
        if ((x in alloweditems) and not(y in alloweditems[x])):
            print ('Wrong value "{0}" for setting {1}: only values accepted are {2}, ignoring.'.format(y,configitems[x],'/'.join(alloweditems[x])))
        if (x in intitems):
            config[x]=int(y)
        elif (x in arrayitems):
            if (not(x in config)):
                config[x]=[]
            config[x].append(y)
        else:
              config[x]=y
        log('--- Setting {0} to {1}'.format(configitems[x],config[x]))
    else:
        log('--- Config item {0} unknown, ignoring'.format(x))
    
def analysis(x):
    global config
    global elements
    
    a=x.split('=')
    if (len(a)==2):
        setconfig(a[0],a[1])
    else:
        elements.append(x)

def addtodisplay(displayed,category,item):
    if not(category in displayed):
        displayed[category]={}
    if item in displayed[category]:
        displayed[category][item]+=1
    else:
        displayed[category][item]=1

def getdisplayed(displayed,category):
    if not(category in displayed):
        return ()
    return sorted(displayed[category].keys())
        


def _(x):
    global langdata
    if x in langdata:
        return langdata[x]
    else:
        return x+' (no text translation)'

def __(x):
    return display_colored(_(x))

def main(argv):
    global data
    global langdata
    global config
    global elements

    for x in sys.argv[1:]:
        analysis(x)
    if not('version' in config):
        with open('lastversion.txt') as lastversionfile:
            num=json.load(lastversionfile)
            config['version']=num
    for file in ('base','fue','olc','wts','war','reserved','cae','arc','epi','holo','prk'):
        importfile(file)
    importlangfile(config['lang'])
    if 'mode' in config:
        mode=config['mode']
    else:
        mode='help'
    xhelp['docs']='Generate all docs in Markdown format'
    if mode == 'docs':
        mode='tournament,crate,unit'
        config['begin']='2012-01-01'
        config['output']='md'
    modes=mode.split(",")
    # Modes in one single phase
    xhelp['tables']='List all tables available in the data files, as well as the number of entries.'
    if ('tables' in modes):
        for t in data:
            print('{0};{1}'.format(t,len(data[t])))
    # Modes in one single phase
    xhelp['translate']='Searches a string ID through the SWC catalog and translates it.'
    morehelp['translate']={'':'keys to be searched  (cumulative, default: all strings)'}
    if ('translate' in modes):
        if len(elements)==0:
            elements=sorted(langdata.keys())
        for t in elements:
            print('{0};{1}'.format(t,_(t)))
    xhelp['table']='List all keys from specific tables'
    morehelp['table']={'table':'table to search keys from (cumulative, default: all tables)','':'keys to be searched'}
    if (mode == 'table'):
        tables=config['table']
        if len(tables)==0:
            tables=data.keys()
        for table in tables:
            if (not(table) in data):
                print('Table unknown {0}'.format(table))
                sys.exit(0)
            for t in data[table]:
                print('{0};{1}'.format(table,t))
    xhelp['tableitem']='List all values from specific tables (specified by table=) and specific items (no items specified is all items) in csv format'
    if (mode == 'tableitem'):
        tables=config['table']
        if len(tables)==0:
            tables=data.keys()
        for table in tables:
            if (not(table) in data):
                print('Table unknown {0}'.format(config[table]))
                sys.exit(1)
            if len(elements)==0:
                xelements=(data[table]).keys()
            else:
                xelements=elements
            for item in xelements:
                if (item in data[table]):
                    for t in data[table][item]:
                        print('{0};{1};{2};{3}'.format(table,item,t,data[table][item][t]))
    # Modes in two phases
    objects={}
    displayed={}
    # Acquisition phase
    ## Tournament
    xhelp['tournament']='Lists all tournaments (conflicts)'
    morehelp['tournament']={'begin':'Start date in format YYYY-MM-DD (default: current day)','end':'End date in format YYYY-MM-DD (default: 9999-12-31)','':'tournament identifier (default: all)'}
    if ('tournament' in modes):
        # do something that adds tournament objects
        for i in data['TournamentData']:
            analyse_tournament(objects,displayed,i)
    ## Crate
    xhelp['crate']='List the contents of crates'
    morehelp['crate']={'planet':'planet the crate is gained from (default: all planets, as with special value "any")','hq':'hq level (default: 5 and 10)','side':'faction (default: all factions, as with special value "any")','':'crate identifier (default: all)'}
    if ('crate' in modes):
        # do something that adds crates objects
        if len(elements)==0:
            xelements=(data['Crate']).keys()
        else:
            xelements=elements
        for i in xelements:
            analyse_crate(objects,displayed,i)
    ## Unit
    xhelp['unit']='List the statistics of units'
    morehelp['unit']={'':'unit identifier (default: all)'}
    if ('unit' in modes):
        # do something that adds tournament objects
        if len(elements)==0:
            tmpdict={}
            for u in (data['TroopData']).keys():
                uname=data['TroopData'][u]['unitID']
                if uname not in tmpdict:
                    tmpdict[uname]=1
            xelements=sorted(tmpdict.keys())
        else:
            xelements=elements
        for i in xelements:
            analyse_unit(objects,displayed,i)
    # Output phase
    out=[]
    outputs=config['output'].split(",")
    if ('tournament' in displayed):
        if ('list' in outputs):
            output_listheader_tournament(out,objects,getdisplayed(displayed,'tournament'))
            dates={}
            for tournament in getdisplayed(displayed,'tournament'):
                dates[objects[tournament]['startDate']+objects[tournament]['endDate']+objects[tournament]['planetId']]=tournament
            for xtournament in sorted(dates):
                tournament=dates[xtournament]
                output_list_tournament(out,objects,objects[tournament])
        if ('csv' in outputs):
            output_csvheader_tournament(out,objects,getdisplayed(displayed,'tournament'))
            for tournament in getdisplayed(displayed,'tournament'):
                output_csv_tournament(out,objects,objects[tournament])
        if ('md' in outputs):
            addtodisplay(displayed,'index','tournament')
            output_mdheader_tournament(out,objects,getdisplayed(displayed,'tournament'))
            for tournament in getdisplayed(displayed,'tournament'):
                output_md_tournament(out,objects,objects[tournament])
    if ('crate' in displayed):
        if ('list' in outputs):
            output_listheader_crate(out,objects,getdisplayed(displayed,'crate'))
            for crate in getdisplayed(displayed,'crate'):
                output_list_crate(out,objects,objects[crate])
        if ('md' in outputs):
            addtodisplay(displayed,'index','crate')
            output_mdheader_crate(out,objects,getdisplayed(displayed,'crate'))
            for crate in getdisplayed(displayed,'crate'):
                output_md_crate(out,objects,objects[crate])
    if ('unit' in displayed):
        if ('list' in outputs):
            output_listheader_unit(out,objects,getdisplayed(displayed,'unit'))
            for unit in getdisplayed(displayed,'unit'):
                output_list_unit(out,objects,objects[unit])            
        if ('md' in outputs):
            addtodisplay(displayed,'index','unit')
            output_mdheader_unit(out,objects,getdisplayed(displayed,'unit'))
            for unit in getdisplayed(displayed,'unit'):
                output_md_unit(out,objects,objects[unit])
    if ('index' in displayed):
        id='index'
        with open("docs/{0}.md".format(id),"w") as file:
            file.write("---\ntitle: {1} ({0})\ncategory: crate\n---\n".format(id,'Main index page'))
            file.write("# {1} ({0}) — version {2}\n\n".format('index','Main index page',config['version']))
            for sid in getdisplayed(displayed,id):
                title='Index of objects of type "{0}"'.format(sid)
                file.write(' * [{1}]({0}.html)\n'.format(sid,title))

    # list mode: print output
    if ('list' in outputs):
        if (len(out)>0):
            print("\n\n".join(out))
    if ('csv' in outputs):
        if (len(out)>0):
            print('\n'.join(out))
    # Help mode
    xhelp['help']='Display this help text.'
    if ('help' in modes):
        print('Usage: swc.py variable=value variable2=value2 ... item1 item2 item3 ...')
        print('Please use mode=xxx with one of these modes')
        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent='    '
        wrapper.subsequent_indent='    '
        morewrapper =  textwrap.TextWrapper()
        morewrapper.initial_indent='      '
        morewrapper.subsequent_indent='      '
        for k,v in xhelp.items():
            print(' * {0}'.format(k))
            print("\n".join(wrapper.wrap(v)))
            if k in morehelp:
                for kk,vv in morehelp[k].items():
                    print("\n".join(wrapper.wrap(' - {0}{2} {1}'.format(kk,vv,('items with no xxx= specifier:' if (kk=='') else '=xxx:')))))
            
    for xmode in modes:
        if (xmode not in xhelp.keys()):
            print('Mode unknown {0}'.format(xmode))
            print("\n".join(xhelp.keys()))
    sys.exit(0)


# This set of functions builds objects from the data, gathering useful data in one place
def variantspace():
    global config
    global data
    sides=[]
    hqs=[]
    planets=[]
    if 'side' in config:
        if config['side']=='any':
            sides=['empire','rebel']
        else:
            sides=[config['side']]
    else:
            sides=['empire','rebel']        
    if 'hq' in config:
        hqs=[config['hq']]
    else:
        hqs=[5,6,7,8,9,10]
    if 'defaultplanet' in config:
        defaultplanet=config['defaultplanet'].split(",")
    else:
        defaultplanet=[]
        for ii in data['ObjSeries']:
            i=data['ObjSeries'][ii]
            if not(i['planetUid'] in defaultplanet):
                defaultplanet.append(i['planetUid'])
        defaultplanet=sorted(defaultplanet)
        config['defaultplanet']=",".join(defaultplanet)
    if 'planet' in config:
        if config['planet']=='any':
            planets=defaultplanet
        else:
            planets=[config['planet']]
    else:
            planets=defaultplanet
    return (sides,hqs,planets)
    
def analyse_crate(objects,displayed,id):
    global data
    global config
    ob={}
    if id in objects:
        ob=objects[id]
    swcitem=data['Crate'][id]
    ob['uid']=swcitem['uid']
    ob['title']='crate_title_'+swcitem['uid']
    if 'expirationTime' in swcitem:
        ob['expirationTime']=swcitem['expirationTime']
    else:
        ob['expirationTime']='never'
    ob['pools']={}
    if 'variants' not in ob:
        ob['variants']={}
    if 'variantsdefaults' not in ob:
        ob['variantsdefaults']={}
    draws=0
    for x in swcitem['supplyPoolUid']:
        if x in ob['pools']:
            ob['pools'][x]+=1
            draws+=1
        else:
            ob['pools'][x]=1
            draws+=1
            if x not in ob['variants']:
                ob['variants'][x]={}
            if x not in ob['variantsdefaults']:
                ob['variantsdefaults'][x]={}
    ob['draws']=draws
    # We do not pass because of variants by hq, planet, side
    (sides,hqs,planets)=variantspace()
    for planet in planets:
        for hq in hqs:
            for side in sides:
                variant='{2},{1},{0}'.format(planet,hq,side)
                if variant not in ob['variants']:
                    analyse_crate_variant(objects,displayed,id,ob,variant,planet,hq,side)
    addtodisplay(displayed,'crate',id)
    if id not in objects:
        objects[id]=ob
    
def analyse_crate_variant(objects,displayed,id,ob,variant,planet,hq,side):
    global data
    global config
    # Fill in pools for specific values of planet, hq, side
    for pool in ob['pools'].keys():
        sensitive={}
        pools={}
        flat=1
        defaults={}
        if 'fallbackUid' in data['CrateSupplyPool'][pool]:
            (fflat,defaults)=analyse_cratepoolitem(hq,data['CrateSupply'][data['CrateSupplyPool'][pool]['fallbackUid']])
        variant='{2},{1},{0}'.format(planet if 'planet' in sensitive else 'any',hq if (fflat==0) else 'any',side if 'faction' in sensitive else 'any')
        ob['variantsdefaults'][pool][variant]=defaults
        instances=0
        for i in data['CrateSupply']:
            item=data['CrateSupply'][i]
            if ('crateSupplyPoolUid' in item) and (pool in item['crateSupplyPoolUid']):
                if ('maxHQ' in item and hq > int(item['maxHQ'])):
                    sensitive['hq']=1
                    continue
                if ('minHQ' in item and hq < int(item['minHQ'])):
                    sensitive['hq']=1
                    continue
                if ('faction' in item and side != item['faction']):
                    sensitive['faction']=1
                    continue
                if ('planet' in item and planet not in item['planet']):
                    sensitive['planet']=1
                    continue
                (xflat,pools[item['uid']])=analyse_cratepoolitem(hq,item)
                if xflat==0:
                    flat=0
                inst=1
                if 'poolInstances' in item:
                    inst=int(item['poolInstances'])
                pools[item['uid']]['rate']=inst
                instances+=inst
        if (flat==0):
            sensitive['hq']=1
        variant='{2},{1},{0}'.format(planet if 'planet' in sensitive else 'any',hq if 'hq' in sensitive else 'any',side if 'faction' in sensitive else 'any')
        ob['variants'][pool][variant]={'items': pools,'instances':instances}

def analyse_cratepoolitem(hq,item):
    global data
    simple_item={}
    simple_item['rewardType']=item['rewardType']
    simple_item['rewardUid']=item['rewardUid']
    flat=1
    if 'scalingUid' in item:
        scale=item['scalingUid']
        xnum=data['CrateSupplyScale'][scale]['HQ10']
        for k in data['CrateSupplyScale'][scale]:
            if data['CrateSupplyScale'][scale][k]!=xnum:
                flat=0
        HQ='HQ{0}'.format(hq)
        # Some scales are missing HQ2.
        try:
            num=data['CrateSupplyScale'][scale]['HQ{0}'.format(hq)]
        except KeyError:
            num=data['CrateSupplyScale'][scale]['HQ3']
    elif 'amount' in item:
        num=item['amount']
    else:
        num='???'
    simple_item['num']=num
    return(flat,simple_item)

def analyse_tournament(objects,displayed,id):
    global data
    global config
    if id in objects:
        return
    ob={}
    def swcdatetoiso(x):
        a=x.split(",")[1]
        (b,c,d)=a.split('-')
        return '{2}-{1}-{0}'.format(b,c,d)
    if id in data['TournamentData']:
        swcitem=data['TournamentData'][id]
        ob['uid']=swcitem['uid']
        ob['title']='tournament_title_'+swcitem['uid']
        ob['endDate']=swcdatetoiso(swcitem['endDate'])
        ob['startDate']=swcdatetoiso(swcitem['startDate'])
        if 'planetId' in swcitem:
            ob['planetId']=swcitem['planetId']
        else:
            ob['planetId']='planet1'
        if 'planet' in config:
            if config['planet']!=ob['planetId']:
                return
        localsd=date.today().isoformat()
        if 'begin' in config:
            localsd=config['begin']
        if 'end' in config:
            localed=config['end']
        else:
            localed='2999-12-31'
        rew={}
        ob['rewards']=rew
        if (ob['startDate']<=localed and ob['endDate']>=localsd):
            addtodisplay(displayed,'tournament',id)
            objects[id]=ob
            if 'rewardGroupId' in swcitem:
                rewardgroup=swcitem['rewardGroupId']
                for rewards in data['TournamentRewards']:
                    if (data['TournamentRewards'][rewards]['tournamentRewardsId'] == rewardgroup):
                        myrew=data['TournamentRewards'][rewards]
                        rew[myrew['tournamentTier']]=myrew['crateRewardUid']
                        oldplanet='any'
                        if 'planet' in config:
                            oldplanet=config['planet']
                        config['planet']=ob['planetId']
                        for crate in myrew['crateRewardUid']:
                            analyse_crate(objects,displayed,crate)
                        if oldplanet != 'any':
                            config['planet']=oldplanet
                        else:
                            del config['planet']


def analyse_unit(objects,displayed,id):
    global data
    global config
    ob={}
    ob['levels']=[]
    ob['hq']={}
    ob['uid']=id
    ob['title']='trp_title_'+id
    ob['unknown']={}
    ob['presentation']={}
    used={'uid':1}
    uparray={'upgradematerials':' All.','upgradecredits':'$', 'upgradecontraband':' Con.','upgradeshards':' data fragments'}
    addtodisplay(displayed,'unit',id)
    for u in (data['TroopData']).keys():
        uname=data['TroopData'][u]['unitID']
        if uname==id:
            subunit=data['TroopData'][u]
            level=int(subunit['lvl'])
            ob['levels'].append(level)
            ob['hq'][level]={}
            ob['presentation'][level]={}
            ob['unknown'][level]={}
            a=ob['hq'][level]
            a=ob['hq'][level]
            xup=[]
            for t in ['upgradeCredits','upgradeMaterials','upgradeContraband','upgradeShards']:
                if t in subunit.keys():
                    a[t]=int(subunit[t])
                else:
                    a[t]=int(0)
                if a[t]>0:
                    xup.append('{0}{1}'.format(a[t],uparray[t.lower()]))
                used[t]=1
            if len(xup)==0:
                a['upgrade']='Nothing'
            else:
                a['upgrade']=', '.join(xup)
            xup=[]
            for t in ['credits','materials','contraband']:
                if t in subunit.keys():
                    a[t]=int(subunit[t])
                else:
                    a[t]=int(0)
                if a[t]>0:
                    xup.append('{0}{1}'.format(a[t],uparray['upgrade'+t]))
                used[t]=1
            if len(xup)==0:
                a['cost']='Free'
            else:
                a['cost']=', '.join(xup)
            for t in ['health','damage','dps','upgradeTime','trainingTime','minAttackRange','maxAttackRange','viewRange','runThreshold','runSpeed','maxSpeed','shieldHealth','shieldCooldown','shieldRange','acceleration']:
                if t in subunit.keys():
                    a[t]=int(round(float(subunit[t])))
                else:
                    a[t]=int(0)
                used[t]=1
            for t in ['isFlying','crushesWalls','playerFacing']:
                if t in subunit.keys():
                    if subunit[t]=='false':
                        a[t]=False
                    else:
                        a[t]=True
                else:
                    a[t]=False
                used[t]=1
            for t in ['faction','type','armorType','role']:
                if t in subunit.keys():
                    a[t]=subunit[t]
                used[t]=1
            for t in ['requirements']:
                if t in subunit.keys():
                    a[t]=subunit[t]
                else:
                    a[t]=[]
                used[t]=1
            targets={}
            for t in config['targettranslation'].keys():
                if t in subunit.keys():
                    a[t]=int(subunit[t])
                else:
                    a[t]=int(0)
                targets[t]=a[t]
                used[t]=1
            tlist=sorted(targets,key=targets.get,reverse=True)
            ttlist=[]
            tmax=targets[tlist[0]]
            for t in tlist:
                if targets[t]==tmax:
                    ttlist.append('**{0} ({1})**'.format(config['targettranslation'][t],targets[t]))
                else:
                    if targets[t]<=50:
                        ttlist.append('{0} ({1})'.format(config['targettranslation'][t],targets[t]))
                    else:
                        ttlist.append('_{0} ({1})_'.format(config['targettranslation'][t],targets[t]))
                a['targets']=', '.join(ttlist)
            used['targetPreferenceString']=1
            used['unitID']=1
            used['lvl']=1
            for t in ['animationDelay','audioAttack','decalSize','iconCameraPosition','factoryScaleFactor','iconCloseupLookatPosition','iconLookatPosition','factoryRotation','audioPlacement','newRotationSpeed','audioDeath','rotationSpeed','iconCloseupCameraPosition','tooltipHeightOffset','buffAssetOffset','gunPosition','gunSequence','assetName','shieldAssetName','bundleName']:
                if t in subunit.keys():
                    ob['presentation'][level][t]=subunit[t]
                used[t]=1
            for t in subunit:
                if t not in used.keys():
                    ob['unknown'][level][t]=subunit[t]
    levels=sorted(ob['hq'].keys())
    ob['firstlevel']=levels[0]
    if len(levels)==1:
        levelstring=str(levels[0])
    else:
        levelstring='{0}-{1}'.format(levels[0],levels[-1])
    for level in ob['hq'].keys():
            ob['hq'][level]['levels']=levelstring
    if id not in objects:
        objects[id]=ob
    
# This set of functions output objects for various modes
def output_listheader_crate(out,objects,displayed):
    out.append("There are {0} crates in the selection:".format(len(displayed)))

def output_list_crate(out,objects,item,LINKS=False):
    global config
    id=item['uid']
    title=__(item['title'])
    xout='\n# {1} ({0}){2}\n\n'.format(id,title," — version {0}".format(config['version']) if LINKS else '')
    xout+='Crates are given as rewards for various actions. The content is revealed only when opening them, by drawing once (or more) in various prize pools. Only one prize is won for each pool per draw. The in-game description of expectations is written manually and can be wrong. The probability of obtaining one prize is indicated below; the pools change according to planet, faction and HQ level.\n\n'
    expiration=display_expiration(item['expirationTime'])
    if (expiration == 'never'):
        xout+='This crates does not expire.'
    else:
        xout+='This crate expires after {0}.'.format(expiration)
    draws=item['draws']
    pools=item['pools']
    if (draws==1):
        xout+=' The contents are one draw from one pool only.'
    elif (draws==len(pools)):
        xout+=' The contents are one draw from each of the {0} pools.'.format(len(pools))
    elif (pools==1):
        xout+=' The contents are {0} draws from one pool.'.format(draws)
    else:
        xout+=' The contents are decided by {0} draws from {1} different pools.'.format(draws,len(pools))
        for i in sorted(pools.keys()):
            xout+='\n  * {0} draw{2} from pool "{1}"'.format(pools[i],i,'s' if pools[i]>1 else '')
    for j in sorted(pools.keys()):
        xout+='\n\n## Pool "{0}" (x{1} draw{2})'.format(j,pools[j],'' if pools[j]<2 else 's')
        thispool={}
        thispooltext={}
        for i in sorted(item['variants'][j]):
            thisvariant=''
#            thisvariant+=
            instances=item['variants'][j][i]['instances']
            lines=[]
            if (instances==0):
                lines.append('  * No items, see the fallback option below')
            for it in item['variants'][j][i]['items']:
                myit=item['variants'][j][i]['items'][it]
                lines.append('  * ({0}/{1}) {2}'.format(myit['rate'],instances,display_unitbatch(myit,LINKS)))
            thisvariant+='\n'+'\n'.join(sorted(lines))
            xhash=hashlib.sha1(thisvariant.encode('utf-8'))
            xxhash=xhash.hexdigest()
            thispooltext[xxhash]=thisvariant
            try:
                thispool[xxhash] += '/{0}'.format(i)
            except KeyError:
                thispool[xxhash]='{0}'.format(i)
        for xxhash in sorted(thispooltext):
            variants=thispool[xxhash]
            xout+='\n\n### {0}\n'.format(display_poolvariant(variants))
            xout+=thispooltext[xxhash]
        for i in sorted(item['variantsdefaults'][j]):
            xout+='\n\n### Fallback{0}\n'.format(display_poolvariant(i,False))
            myit=item['variantsdefaults'][j][i]
            xout+='\n  * {0}'.format(display_unitbatch(myit,LINKS))
    out[len(out)-1]+=xout

def output_mdheader_crate(out,objects,displayed):
    with open("docs/crate.md","w") as file:
        file.write("---\ntitle: Index of crates\n---\n")
        file.write("# Crates — version {0}\n\n".format(config['version']))
        for crate in displayed:
            item=objects[crate]
            id=item['uid']
            title=__(item['title'])
            file.write("  * [{1} ({0})]({0}.html)\n".format(id,title))

def output_md_crate(out,objects,item):
    id=item['uid']
    title=__(item['title'])
    with open("docs/{0}.md".format(id),"w") as file:
        file.write("---\ntitle: {1} ({0})\ncategory: crate\n---\n".format(id,title))
        lout=['']
        output_list_crate(lout,objects,item,True)
        file.write(lout[0])


def output_listheader_tournament(out,objects,displayed):
    out.append("There are {0} tournaments in the selection:".format(len(displayed)))

def output_list_tournament(out,objects,item):
    rewards=item['rewards']
    rewardsstr=''
    leagues={'tournament_tier_8':'ULTRACHROME','tournament_tier_7':'OBSIDIAN','tournament_tier_6':'BRONZIUM_01','tournament_tier_5':'BRONZIUM_02','tournament_tier_4':'DURASTEEL_01','tournament_tier_3':'DURASTEEL_02','tournament_tier_2':'CARBONITE_01','tournament_tier_1':'CARBONITE_02'}
    if len(rewards)>0:
        rewardsstr=' The rewards are:'
        for k in sorted(rewards.keys()):
            if len(rewards[k])==1:
                rewardsstr+='\n    * {1}: crate "{2}"'.format(k,_('TOURNAMENT_TIER_'+leagues[k]),rewards[k][0])
            else:
                rewardsstr+='\n    * {1}: '.format(k,_('TOURNAMENT_TIER_'+leagues[k]))
                crates={}
                for j in rewards[k]:
                    if j in crates:
                        crates[j]+=1
                    else:
                        crates[j]=1
                for j,k in crates.items():
                    if k==1:
                        rewardsstr+='crate "{1}"'.format(k,display_crate_veryshort(j))
                    else:
                        rewardsstr+='{0} crates "{1}"'.format(k,display_crate_veryshort(j))
                rewardsstr+=''
    xout='\n  * A tournament "{4}" ({0}) that begins on {1} and ends on {2} on planet {3}.{5}'.format(item['uid'],item['startDate'],item['endDate'],display_planet(item['planetId']),_(item['title']),rewardsstr)
    out[len(out)-1]+=xout

def output_csvheader_tournament(out,objects,displayed):
    out.append('#id;planet;startDate;endDate;reward1;reward2;reward3;reward4;reward5;reward6;reward7;reward8')

def output_csv_tournament(out,objects,item):
    rewards=item['rewards']
    ar=['','','','','','','','']
    for i in range(1,9):
        tier='tournament_tier_{0}'.format(i)
        if tier in rewards:
            ar[i-1]=','.join(rewards[tier])
        else:
            print('no reward '+tier)
    xout=";".join([item['uid'],display_planet(item['planetId']),item['startDate'],item['endDate']]+ar)
    out[len(out)-1]+='\n'+xout

def output_mdheader_tournament(out,objects,displayed):
    with open("docs/tournament.md","w") as file:
        file.write("---\ntitle: Index of conflicts\n---\n")
        file.write("# Conflicts — version {0}\n\n".format(config['version']))
        dates={}
        for tournament in displayed:
            dates[objects[tournament]['startDate']+objects[tournament]['endDate']+objects[tournament]['planetId']]=tournament
        for xtournament in reversed(sorted(dates)):
            tournament=dates[xtournament]
            item=objects[tournament]
            id=item['uid']
            title=__(item['title'])
            file.write("  * [{1} ({0})]({0}.html)\n".format(id,title))

def output_md_tournament(out,objects,item):
    id=item['uid']
    title=__('tournament_title_'+id)
    with open("docs/{0}.md".format(id),"w") as file:
        file.write("---\ntitle: {1} ({0})\ncategory: tournament\n---\n".format(id,title))
        file.write("# {0}\n\n  * Start date: {1}\n  * End date: {2}\n\n".format(title,item['startDate'],item['endDate']))
        file.write("## Rewards\n\n")
        rewards=item['rewards']
        rewardsstr=''
        leagues={'tournament_tier_8':'ULTRACHROME','tournament_tier_7':'OBSIDIAN','tournament_tier_6':'BRONZIUM_01','tournament_tier_5':'BRONZIUM_02','tournament_tier_4':'DURASTEEL_02','tournament_tier_3':'DURASTEEL_01','tournament_tier_2':'CARBONITE_01','tournament_tier_1':'CARBONITE_02'}
        if len(rewards)>0:
            for k in sorted(rewards.keys()):
                file.write('  * {1}:'.format(k,_('TOURNAMENT_TIER_'+leagues[k])))
                crates={}
                for j in rewards[k]:
                    if j in crates:
                        crates[j]+=1
                    else:
                        crates[j]=1
                head=' '
                if len(crates.keys())>1:
                    file.write('\n')
                    head='    * '
                for j,k in crates.items():
                    if k==1:
                        file.write(head+'A "{1}"'.format(k,display_crate_mdlink(j,'')))
                    else:
                        file.write(head+'{0} "{1}"'.format(k,display_crate_mdlink(j,'s')))
                file.write('\n')
            file.write(rewardsstr)
    

def output_listheader_unit(out,objects,displayed):
    out.append("There are {0} units in the selection:".format(len(displayed)))

def output_list_unit(out,objects,item,LINKS=False):
    global config
    id=item['uid']
    title=__(item['title'])
    levels=sorted(item['levels'])
    xout='\n# {1} ({0}){2}\n\n'.format(id,title," — version {0}".format(config['version']) if LINKS else '')
    firstlevel=levels[0]
    xout+='## Main stats\n\n'
    handlers={'upgradeTime':display_time,'trainingTime':display_time}
    handlers['faction']=display_side
    handlers['playerFacing']=display_boolean
    xout+=display_leveldata(item['hq'],levels,['faction','playerFacing','type','armorType','role','levels','upgrade','upgradeTime','health','damage','dps','shieldHealth','shieldCooldown','shieldRange'],{'levels':'Levels available','playerFacing': 'Buildable unit','upgrade': 'Upgrade requirements','upgradeTime':'Upgrade time','health':'Health','damage':'Damage*','dps':'Damage per second*','role':'Role','type':'Type','armorType':'Armor type','faction':'Side','shieldHealth':'Shield Health','shieldCooldown':'Shield Cooldown','shieldRange':'Shield Range'},handlers)

    xout+='* These values are not necessarily accurate and may be inconsistent with other values\n\n## Targetting\n\n'
    translation=config['targettranslation']
    list=[x for x in sorted(translation,key=translation.get)]
    list=['targets','maxAttackRange','minAttackRange','viewRange']
    translation['targets']='Target preferences'
    translation['maxAttackRange']='Max. Range'
    translation['minAttackRange']='Min. Range'
    translation['viewRange']='View Range'
    xout+=display_leveldata(item['hq'],levels,list,translation,{})
    xout+='## Recruiting\n\n'
    translation={'cost':'Training cost','trainingTime': 'Training time'}
    req=0
    for l in levels:
        ll=len(item['hq'][l]['requirements'])
        if ll>req:
            req=ll
    list=['cost','trainingTime']
    for ll in range(0,req):
        r='requirement'+str(ll)
        list.append(r)
        translation[r]='Building '+str(ll)
        if req==1:
            translation[r]='Building'
        for l in levels:
            a=item['hq'][l]['requirements']
            if ll<len(a):
                item['hq'][l][r]=display_building(a[ll],LINKS)
            else:
                item['hq'][l][r]='None'
    handlers={}
    xout+=display_leveldata(item['hq'],levels,list,translation,handlers)
    xout+='## Movement\n\n'
    translation={'maxSpeed':'Speed','runSpeed':'Run speed','runThreshold':'Run Threshold','isFlying':'Flying unit','acceleration':'Acceleration','crushesWalls':'Crushes walls'}
    list=['maxSpeed','runSpeed','runThreshold','isFlying','acceleration','crushesWalls']
    handlers={'isFlying':display_boolean,'crushesWalls':display_boolean}
    xout+=display_leveldata(item['hq'],levels,list,translation,handlers)
    xout+='## Presentation stats\n\nThese graphical elements shouldn\'t interfere with gameplay and can safely be ignored.\n\n'
    items=item['presentation'][firstlevel].keys()
    translation={}
    for i in items:
        translation[i]=i
    xout+=display_leveldata(item['presentation'],levels,items,{},{})
    xout+='## Uninterpreted stats\n\n'
    items=item['unknown'][firstlevel].keys()
    translation={}
    for i in items:
        translation[i]=i
    xout+=display_leveldata(item['unknown'],levels,items,{},{'pointValue':lambda x:('%.3f' % float(x))})
#    xout+='{0}'.format(item['hq'][firstlevel])
    out[len(out)-1]+=xout

def output_mdheader_unit(out,objects,displayed):
    with open("docs/unit.md","w") as file:
        file.write("---\ntitle: Index of units\n---\n")
        file.write("# Units — version {0}\n\n".format(config['version']))
        pfd={True:'Buildable units',False:'Other units'}
        for pf in [True, False]:
            file.write("## {0}\n\n".format(pfd[pf]))
            sides={}
            for unit in displayed:
                item=objects[unit]
                firstlevel=item['firstlevel']
                if item['hq'][firstlevel]['playerFacing']==pf:
                    sides[item['hq'][firstlevel]['faction']]=1
            for side in sorted(sides):
                file.write("### {0}\n\n".format(display_side(side)))
                for unit in displayed:
                    item=objects[unit]
                    firstlevel=item['firstlevel']
                    if item['hq'][firstlevel]['playerFacing']==pf:
                        if item['hq'][firstlevel]['faction']==side:
                            id=item['uid']
                            title=__(item['title'])
                            file.write("  * [{1} ({0})]({0}.html)\n".format(id,title))
                file.write("\n")

def output_md_unit(out,objects,item):
    id=item['uid']
    title=__(item['title'])
    with open("docs/{0}.md".format(id),"w") as file:
        file.write("---\ntitle: {1} ({0})\ncategory: unit\n---\n".format(id,title))
        lout=['']
        output_list_unit(lout,objects,item,True)
        file.write(lout[0])


# This set of functions take an Id and return the adequate string for it

def display_planet(planetId):
    return _('planet_name_'+planetId)

def display_boolean(x):
    if x:
        return 'Yes'
    return 'No'

def display_side(side):
    if (side=='empire'):
        return 'Empire'
    if (side=='rebel'):
        return 'Rebellion'
    if (side=='smuggler'):
        return 'Independant units'
    if (side=='tusken'):
        return 'Tusken Raiders'
    if (side=='neutral'):
        return 'Other units'
    return side

def display_crate_veryshort(crateId):
    return crateId

def display_crate_mdlink(crateId,plural):
    return '[{1}{2} ({0})]({0}.html)'.format(crateId,_('crate_title_'+crateId),plural)

def display_colored(string):
        return re.sub("\[.*\]", '', string)

def display_expiration(s):
    if (s=='never'):
        return s
    a=int(s)
    days=int(a/1440)
    hours=int((a%1440)/60)
    minutes=int(a%60)
    x=''
    if days>0:
        x='{0}d'.format(days)
    if (hours+minutes)>0:
        x+='{0:02d}h'.format(hours)
    if minutes>0:
        x+='{0:02d}m'.format(minutes)
    return x

def display_time(s,micro=False):
    t=[]
    if micro:
        hsecs=s%100
        s=int((s-hsecs)/100)
    sec=s%60
    s=int((s-sec)/60)
    min=s%60
    s=int((s-min)/60)
    hour=s%24
    s=int((s-hour)/24)
    day=s%7
    s=int((s-day)/7)
    out=''
    if (s>0):
        out+='{0}w'.format(s)
    if (day>0):
        out+='{0}d'.format(day)
    if (hour>0):
        out+='{0}h'.format(hour)
    if (min>0):
        out+='{0}m'.format(min)
    if (sec>0):
        if micro:
            if hsecs>10:
                out+='{0}.{1}'.format(sec,hsecs)
            elif hsecs>0:
                out+='{0}.0{1}'.format(sec,hsecs)
            else:
                out+='{0}s'.format(sec)
        else:
            out+='{0}s'.format(sec)
    if (out==''):
        return('0s')
    return(out)

def display_microtime(s):
    return display_time(s,True)

def display_poolvariant(variants,cap=True):
    variantsarray=variants.split('/')
    def describehq(space,levels,cap):
        s2=':'.join([str(l) for l in sorted(space)])
        if levels==s2:
            return ''
        else:
            xlevels=[]
            for l in levels.split(':'):
                xlevels.append(int(l))
            xlevels.sort()
        pairs=[]
        num=len(xlevels)
        while len(xlevels)>0:
            start=xlevels[0]
            current=start
            while (current in xlevels):
                xlevels.remove(current)
                current+=1
            stop=current-1
            if stop==start:
                pairs.append('{0}'.format(start))
            else:
                pairs.append('{0}-{1}'.format(start,stop))
        if pairs[0]=='2-10':
            return ''
        if cap:
            sentence='For HQ'
        else:
            sentence=' for HQ'
        if (num>1):
            sentence+=' levels '
        else:
            sentence+=' level '
        sentence+=', '.join(pairs)
        return sentence
    
    def describeplanet(space,planets,cap):
        if planets==':'.join(space):
            return ''
        planetsarr=planets.split(':')
        if planetsarr[0]=='any':
            return ''
        if cap:
            sentence='On '
        else:
            sentence=' on '
        planetnames=[]
        for p in planetsarr:
            planetnames.append(display_planet(p))
        return sentence+' or '.join(sorted(planetnames))
    
    def describefaction(space,factions,cap):
        if factions==':'.join(space):
            return ''
        prefix='' if cap else ' '
        factionsarr=factions.split(':')
        far=[display_side(f) for f in factionsarr]
        return prefix+(' or '.join(far))

    (sides,hqs,planets)=variantspace()
    poolbysidebyplanet={}
    for s in variantsarray:
        (side,hq,planet)=s.split(',')
        if side in poolbysidebyplanet:
            if planet in poolbysidebyplanet[side]:
                pass
            else:
                poolbysidebyplanet[side][planet]={}
        else:
            poolbysidebyplanet[side]={}
            poolbysidebyplanet[side][planet]={}
        if hq=='any':
            for h in hqs:
                hh='{0}'.format(h)
                poolbysidebyplanet[side][planet][hh]=1
        else:
                poolbysidebyplanet[side][planet][hq]=1
    variantsarray=[]
    for side in poolbysidebyplanet.keys():
        for planet in poolbysidebyplanet[side].keys():
            thqs=sorted(poolbysidebyplanet[side][planet].keys(),key=int)
            variantsarray.append('{2},{1},{0}'.format(planet,':'.join(thqs),side))
    poolbysidebyhq={}
    for s in variantsarray:
        (side,hq,planet)=s.split(',')
        if side in poolbysidebyhq:
            if hq in poolbysidebyhq[side]:
                pass
            else:
                poolbysidebyhq[side][hq]={}
        else:
            poolbysidebyhq[side]={}
            poolbysidebyhq[side][hq]={}
        if planet=='any':
            for p in planets:
                poolbysidebyhq[side][hq][p]=1
        else:
                poolbysidebyhq[side][hq][planet]=1
    variantsarray=[]
    for side in poolbysidebyhq.keys():
        for planet in poolbysidebyhq[side].keys():
            pl=sorted(poolbysidebyhq[side][hq].keys())
            variantsarray.append('{2},{1},{0}'.format(':'.join(pl),hq,side))
    poolbyplanetbyhq={}
    for s in variantsarray:
        (side,hq,planet)=s.split(',')
        if planet in poolbyplanetbyhq:
            if hq in poolbyplanetbyhq[planet]:
                pass
            else:
                poolbyplanetbyhq[planet][hq]={}
        else:
            poolbyplanetbyhq[planet]={}
            poolbyplanetbyhq[planet][hq]={}
        if side=='any':
            for si in sides:
                poolbyplanetbyhq[planet][hq][si]=1
        else:
                poolbyplanetbyhq[planet][hq][side]=1
    variantsarray=[]
    for planet in poolbyplanetbyhq.keys():
        for hq in poolbyplanetbyhq[planet].keys():
            si=sorted(poolbyplanetbyhq[planet][hq].keys())
            variantsarray.append('{2},{1},{0}'.format(planet,hq,':'.join(si)))
    pieces=[]
    ocap=cap
    for s in variantsarray:
        final=''
        (side,hq,planet)=s.split(',')
        f=describefaction(sides,side,cap)
        if len(f)>0:
            cap=False
        final=f
        f=describeplanet(planets,planet,cap)
        if len(f)>0:
            cap=False
        final+=f
        f=describehq(hqs,hq,cap)
        if len(f)>0:
            cap=False
        final+=f
        pieces.append(final)
    final=' or '.join(pieces)
    if final=='':
        if cap:
            final='Always'
    return final

def display_building(i,link):
    global data
    global config
    r=data['BuildingData'][i]['buildingID']
    level=data['BuildingData'][i]['lvl']
    if link:
        r='[{0} {2}]({1}.html)'.format(_('bld_title_'+r),r,level)
    else:
        r='{0} {2}'.format(_('bld_title_'+r),r,level)
    return r

def display_unitbatch(item,link):
    count=item['num']
    nature=''
    itemx=''
    title=''
    line='{0} {1} {2}'
    if link:
        line='{0} {1} [{2}]({3})'
    if (item['rewardType'] == 'currency'):
        array={'contraband': _('CONTRABAND'), 'crystals':_('CRYSTALS'),'materials':_('MATERIALS'),'credits':_('CREDITS'), 'reputation':_('REPUTATION')}
        nature='resource'
        itemx=array[item['rewardUid']]
        line='{0} {3}'
    elif (item['rewardType'] == 'shard'):
        nature='data fragments of equipment'
        itemx=item['rewardUid']
        title=_(display_things(item['rewardUid'],'EquipmentData','equipmentID','equipmentName'))
    elif (item['rewardType'] == 'shardTroop'):
        nature='data fragments of unlockable troop'
        itemx=display_things(item['rewardUid'],'TroopData','upgradeShardUid','unitID')
        title=_('trp_title_'+itemx)
    elif (item['rewardType'] == 'shardSpecialAttack'):
        nature='data fragments of unlockable air support'
        itemx=display_things(item['rewardUid'],'SpecialAttackData','upgradeShardUid','specialAttackID')
        title=_('shp_title_'+itemx)
    elif (item['rewardType'] == 'troop'):
        nature='troop sample'
        itemx=display_things(item['rewardUid'],'TroopData','uid','unitID')
        title=_('trp_title_'+itemx)
    elif (item['rewardType'] == 'specialAttack'):
        nature='air support sample'
        itemx=display_things(item['rewardUid'],'SpecialAttackData','uid','specialAttackID')
        title=_('shp_title_'+itemx)
    elif (item['rewardType'] == 'hero'):
        nature='hero sample of'
        itemx=display_things(item['rewardUid'],'TroopData','uid','unitID')
        title=_('trp_title_'+itemx)
    else:
        nature=item['rewardType']
        itemx=name
        line='{0} {1}: {2}'
    if title=='':
        title=itemx
    line=line.format(count,nature,title,itemx)
    return(line)

def display_things(uid,table,localid,localname):
    global data
    for xx in data[table]:
        x=data[table][xx]
        if ((localid in x) and (localname in x) and (x[localid]==uid)):
            return x[localname]
    return uid

def display_leveldata(data,levels,keys,titles,funcs,LINKS=False):
    commonvalues=[]
    variablevalues=[]
    display={}
    firstlevel=levels[0]
    for key in keys:
        if key in funcs:
            func=funcs[key]
        else:
            func=str
        display[key]={}
        identical=True
        dataitem=data[firstlevel][key]
        for level in levels:
            if key in data[level]:
                display[key][level]=func(data[level][key])
                if data[level][key]!=dataitem:
                    identical=False
            else:
                display[key][level]='(not found)'
                identical=False
        if identical:
            commonvalues.append(key)
        else:
            variablevalues.append(key)
    output=''
    for key in commonvalues:
        t=key
        if key in titles:
            t=titles[key]
        output+='  * {0}: {1}\n'.format(t,display[key][firstlevel])
    width={}
    width['label']=5
    for level in levels:
        width[level]=2
        for key in variablevalues:
            w=len(display[key][level])
            if w>width[level]:
                width[level]=w
    for key in variablevalues:
        t=key
        if key in titles:
            t=titles[key]
        w=len(t)
        if w>width['label']:
            width['label']=w
    if len(output)>0:
        output+='\n'
    if len(variablevalues)>0:
        line='|'
        line+='{message: <{width}}|'.format(message='Level',width=width['label'])
        for level in levels:
            line+='{message: <{width}}|'.format(message=str(level),width=width[level])
        line+='\n|'
        line+=('-'*width['label'])+'|'
        for level in levels:
            line+=('-'*width[level])
            line+='|'
        line+='\n'
        for key in variablevalues:
            t=key
            if key in titles:
                t=titles[key]
            line+='|'
            line+='{message: <{width}}|'.format(message=t,width=width['label'])
            for level in levels:
                line+='{message: <{width}}|'.format(message=display[key][level],width=width[level])
            line+='\n'
        output+=line+'\n'
    return(output)

if __name__ == "__main__":
#    print(display_leveldata({0:{'speed':50,'val':8,'age':12, 'sex':'M'},1:{'speed':50,'val':8,'age':14,'sex':'M'},2:{'speed':50,'val':9,'age':20,'sex':'M'}},[0,1,2],['val','age','sex','speed'],{'val':'Value','age':'Age','sex':'Gender','speed':'Speed'},{}))
#    sys.exit(0)
    main(sys.argv)
