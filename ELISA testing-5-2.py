from opentrons import protocol_api
from opentrons import simulate
protocol = simulate.get_protocol_api('2.15')

metadata = {'apiLevel': '2.15',
               'protocolName':'ELISA protocol group 4',
    'description': '''This protocol is to implement the iGem protocol. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate.''',
    'author': 'Group Four'}

def run(protocol:protocol_api.ProtocolContext):

    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    tiprack_3 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    tiprack_4 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    tiprack_5 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)

    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1,tiprack_2,tiprack_3,tiprack_4,tiprack_5])
    p300.flow_rate.aspirate = 30   

    p300.well_bottom_clearance.aspirate = 5
    p300.well_bottom_clearance.dispense = 5
   
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 1)
    plate = protocol.load_labware('thermofischer_96_wellplate_400ul', 3)
    deep_well = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)
    trash = protocol.load_labware('usascientific_12_reservoir_22ml', 11)

    #magnetic module
    mag_mod = protocol.load_module('magnetic module', 7)
    mag_adapter = mag_mod.load_adapter('opentrons_96_flat_bottom_adapter')
    mag_rack = mag_mod.load_labware('thermofischer_96_wellplate_400ul')

    #A1 reservoir is 2M NaOH
    #A2 will ahve over 4 mL of equilibration buffer
    #A3 will have pre allocated 200 uL of beads - then buffer added ot this to make bead slurry
    #A4 is the wash buffer for the beads
    #A5 is elution buffer for beads
    #A6 is coating solution 
    #A7 is blocking buffer
    #A8 is PBS
    #A9 is primary antibody
    #A10 is secondary antibody
    #A11 is PnPP
    
    #take 800 uL fro deep well plate and put into a new column 
   # p300.transfer(800, deep_well.rows()[0][:2], deep_well.rows()[0][2:4])#, mix_after=(3, 50))

    #add 80 uL of NaOH to those columns
 #   p300.transfer(80, reservoir["A1"], deep_well.rows()[0][2:4])#, mix_after=(3, 50))
    #delay an hour
    #now add 300 uL of each of these to two separate columns
    #samples 1-8
#    p300.transfer(300, deep_well.rows()[0][2], deep_well.rows()[0][4:6])#, mix_after=(3, 50))
    #samples 9-16
#    p300.transfer(300, deep_well.rows()[0][3], deep_well.rows()[0][6:8])#, mix_after=(3, 50))
    

    
    #make the beads 
    p300.transfer(1800, reservoir["A1"], reservoir["A3"], mix_after=(3, 50))
    #transfer beads to mag plate
    p300.transfer(1900, reservoir["A3"], mag_rack.rows()[0][0], mix_before=(3, 50))
    mag_mod.engage(height_from_base=4.4)
    #delay two minutes to let the beads get washed
    protocol.delay(minutes = 2)
    #dump out 500 uL of this to trash
    p300.transfer(1900/8, mag_rack.rows()[0][0], trash["A1"])#, mix_after=(3, 50))
    mag_mod.disengage()       
    #add new 950 mL of equil buffer to beads
    p300.transfer(950, reservoir["A2"], mag_rack.rows()[0][0], mix_after=(3, 50))
    
    #add the beads
    p300.transfer(30, mag_rack.rows()[0][0], mag_rack.rows()[0][1:5], mix_before=(3, 50)) 

    #delay 5 minutes to equilibriate with teh DNA
    #transfer beads to mag plate
    p300.transfer(60, deep_well.rows()[0][4:8],mag_rack.rows()[0][1:5], mix_after=(3, 50)) 
    mag_mod.engage(height_from_base=4.4)
    #wait 3 minutes
    p300.transfer(660, mag_rack.rows()[0][1:5], trash["A1"], mix_after=(3, 50))
    mag_mod.disengage()       
    #add wash buffer
    p300.transfer(300, reservoir["A4"], mag_rack.rows()[0][1:5], mix_after=(3, 50))
    mag_mod.engage(height_from_base=4.4)
    #wait 2 mintues
    p300.transfer(300, mag_rack.rows()[0][1:5], trash["A1"], mix_after=(3, 50))
    mag_mod.disengage()       
    p300.transfer(300, reservoir["A4"], mag_rack.rows()[0][1:5], mix_after=(3, 50))
    mag_mod.engage(height_from_base=4.4)
    #wait 2 mintues
    p300.transfer(300, mag_rack.rows()[0][1:5], trash["A1"], mix_after=(3, 50))
    mag_mod.disengage()
    #elution buffer
    p300.transfer(100, reservoir["A5"], mag_rack.rows()[0][1:5], mix_after=(3, 50))
    
    p300.transfer(100, mag_rack.rows()[0][1:3],deep_well.rows()[0][9], mix_after=(3, 50))
    p300.transfer(100, mag_rack.rows()[0][3:5],deep_well.rows()[0][10], mix_after=(3, 50))
    
    #wait ten minutes
    #add eluted sample abck to mag rack
    p300.transfer(200, deep_well.rows()[0][9:10],mag_rack.rows()[0][5:7], mix_after=(3, 50))
    #wait two mintues to pull out beads
    
    
    ######### ELISA PROTOCOL ############
    #setting up the dilution plate
    #adding the antigen solution to col 1
    p300.transfer(200, mag_rack.rows()[0][5:7], plate.rows()[0][:1], mix_after=(3, 50))
    #adding the coating solution to the other wells for the serial dilutions
    p300.transfer(100, reservoir["A6"], plate.rows()[0][1:6])
    #making dilutions from col 1 to col 5
    p300.transfer(100, plate.rows()[0][:5], plate.rows()[0][1:6], mix_after=(3, 50))
    #empty the extra 100 uL from col 6
    p300.transfer(100, plate.rows()[0][5], trash["A1"])#, mix_after=(3, 50))

    #wait for 2 hours at room temp - at this time, flip the tiprack so that new tips are on the left - now shoudl have 8 cols left
    p300.transfer(100, plate.rows()[0][:5], trash["A1"])#, mix_after=(3, 50))
    #will need to drop tips after each of these



    #add 200 uL blocking buffer to every well
    p300.transfer(200, reservoir["A7"], plate.rows()[0][:6])
    #wait 1-2 hours at room temp
    #dump out blockign buffer
    p300.transfer(200,plate.rows()[0][:6], trash["A1"])

    #wash with 100 uL of PBS 3 times
    for wash in range(3):
        p300.transfer(100,reservoir["A8"] , plate.rows()[0][:6], mix_after=(1, 50))
        p300.transfer(100,plate.rows()[0][:6], trash["A1"])

    #chekc how much volume to use per wash

    #add 100 uL primary antibody to every well
    p300.transfer(100, reservoir["A9"], plate.rows()[0][:6])
    #wait 1-2 hours
    #dump out solution
    p300.transfer(100,plate.rows()[0][:6], trash["A2"])
    #wash with 100 uL of PBS 3 times
    for wash in range(3):
        p300.transfer(100,reservoir["A8"] , plate.rows()[0][:6], mix_after=(1, 50))
        p300.transfer(100,plate.rows()[0][:6], trash["A2"])


    #add 100 uL secondary antibody to every well
    p300.transfer(100, reservoir["A10"], plate.rows()[0][:6])
    #wait 1-2 hours
    #dump out solution
    p300.transfer(100,plate.rows()[0][:6], trash["A2"])

    #add PBS and agitate for 5 minutes
    p300.transfer(100,reservoir["A8"] , plate.rows()[0][:6], mix_after=(1, 50))
    ###AGITATE FOR 5 MINUTES#####
    p300.transfer(100,plate.rows()[0][:6], trash["A2"])
    #wash with 100 uL of PBS 3 times
    for wash in range(3):
        p300.transfer(100,reservoir["A8"] , plate.rows()[0][:6], mix_after=(1, 50))
        p300.transfer(100,plate.rows()[0][:6], trash["A2"])

    #mix the PNPP by hand then add to reservoir column A11
    p300.transfer(100, reservoir["A11"], plate.rows()[0][:6], mix_after=(3, 50))
    #incubate fro 15- 30 minutes
    #add 50 uL of NaOH
    p300.transfer(50, reservoir["A1"], plate.rows()[0][:6], mix_after=(3, 50))

    return
