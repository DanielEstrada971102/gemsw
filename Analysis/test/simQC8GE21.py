import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
process = cms.Process('tb',eras.phase2_muon)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedGauss_cfi')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
# test beam detectors at y-axis - GE21 at (0,110*cm,0), GE0 at (0,120*cm,0)
process.load('gemsw.Geometry.GeometryQC8GE21_cff')
process.load('MagneticField.Engine.uniformMagneticField_cfi')

SuperChType = ['S','0','0','0','0','0','S']
print(SuperChType)

# SuperChSeedingLayers = []

# for i in range (0,30):
#     SuperChSeedingLayers.append(0)

# for j in range (0,3):
#     for i in range (5*j,5*(j+1)):
#         if (SuperChType[i]!='0'):
#             SuperChSeedingLayers[i*2]=1
#             SuperChSeedingLayers[i*2+1]=3
#             break
#     for i in range (5*(j+1)-1,5*j-1,-1):
#         if (SuperChType[i]!='0'):
#             SuperChSeedingLayers[i*2]=4
#             SuperChSeedingLayers[i*2+1]=2
#             break

SuperChSeedingLayers = [1,3,0,0,0,4,2]
print(SuperChSeedingLayers)


process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000), #Number events
)
process.source = cms.Source("EmptySource")
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('TenMuExtendedE_0_200_pythia8_cfi nevts:10'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

process.FEVTDEBUGoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:step1.root'),
    outputCommands = cms.untracked.vstring( (
        'keep *',
        'keep FEDRawDataCollection_rawDataCollector_*_*',
        'keep *_gemRecHits_*_*',
        'keep *_gemSegments_*_*',
        'keep *_muonGEMDigis_*_*',
        'keep *DigiSimLinkedmDetSetVector_simMuonGEMDigis_*_*',
        'keep *_simMuonGEMDigis_*_*',
        'keep *_genParticles_*_*',
        'keep *_g4SimHits_MuonGEMHits_*',
        'keep *_g4SimHits__*',
    )),
    splitLevel = cms.untracked.int32(0)
)

# Cosmic Muon generator
process.generator = cms.EDProducer("CosmicGun",
    AddAntiParticle = cms.bool(True),
    PGunParameters = cms.PSet(
        MinPt = cms.double(99.99),
        MaxPt = cms.double(100.01),
        MinPhi = cms.double(3.141592),
        MaxPhi = cms.double(-3.141592),
        MinTheta = cms.double(1.570796),
        MaxTheta = cms.double(3.141592),
        IsThetaFlat = cms.bool(False), # If 'True': theta distribution is flat. If 'False': theta distribution is a cos^2
        PartID = cms.vint32(-13)
    ),
    Verbosity = cms.untracked.int32(0),
    firstRun = cms.untracked.uint32(1),
    psethack = cms.string('single mu pt 100')
)

process.g4SimHits.UseMagneticField = cms.bool(False)
process.g4SimHits.OnlySDs = cms.vstring('MuonSensitiveDetector')
process.g4SimHits.Physics.CutsPerRegion = cms.bool(False)

process.mix = cms.EDProducer("MixingModule",
    digitizers = cms.PSet(),
    # LabelPlayback = cms.string(''),
    maxBunch = cms.int32(3),
    minBunch = cms.int32(-5), ## in terms of 25 ns
    bunchspace = cms.int32(450),
    mixProdStep1 = cms.bool(False),
    mixProdStep2 = cms.bool(False),
    # playback = cms.untracked.bool(False),
    # useCurrentProcessOnly = cms.bool(False),
    mixObjects = cms.PSet(
        mixSH = cms.PSet(
            crossingFrames = cms.untracked.vstring('MuonGEMHits',),
            input = cms.VInputTag(cms.InputTag("g4SimHits","MuonGEMHits")),
            type = cms.string('PSimHit'),
            subdets = cms.vstring('MuonGEMHits'),
        ),
    ),
)
process.GEMCosmicMuonForQC8 = cms.EDProducer("GEMCosmicMuonForQC8",
                                       process.MuonServiceProxy,
                                       gemRecHitLabel = cms.InputTag("gemRecHits"),
                                       maxClusterSize = cms.double(10),
                                       minClusterSize = cms.double(1),
                                       trackChi2 = cms.double(1000.0),
                                       trackResX = cms.double(100),
                                       trackResY = cms.double(100),
                                       MulSigmaOnWindow = cms.double(7),
                                       SuperChamberType = cms.vstring(SuperChType),
                                       SuperChamberSeedingLayers = cms.vdouble(SuperChSeedingLayers),
                                       MuonSmootherParameters = cms.PSet(
                                           PropagatorAlong = cms.string('SteppingHelixPropagatorAny'),
                                           PropagatorOpposite = cms.string('SteppingHelixPropagatorAny'),
                                           RescalingFactor = cms.double(5.0)
                                           ),
                                       )
process.GEMCosmicMuonForQC8.ServiceParameters.GEMLayers = cms.untracked.bool(True)
process.GEMCosmicMuonForQC8.ServiceParameters.CSCLayers = cms.untracked.bool(False)
process.GEMCosmicMuonForQC8.ServiceParameters.RPCLayers = cms.bool(False)
process.gemPacker.useDBEMap = False

process.rawDataCollector.RawCollectionList = cms.VInputTag(cms.InputTag("gemPacker"))

process.muonGEMDigis.readMultiBX = True
process.muonGEMDigis.useDBEMap = process.gemPacker.useDBEMap
process.muonGEMDigis.keepDAQStatus = True
process.gemRecHits.gemDigiLabel = cms.InputTag('simMuonGEMDigis')

process.generation_step = cms.Path(process.generator+process.pgen)
process.simulation_step = cms.Path(process.psim)
process.digitisation_step = cms.Path(process.mix+process.simMuonGEMDigis)
#process.digi2raw_step = cms.Path(process.gemPacker+process.rawDataCollector+process.muonGEMDigis+process.gemRecHits)
process.digi2raw_step = cms.Path(process.gemRecHits* process.GEMCosmicMuonForQC8)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGoutput_step = cms.EndPath(process.FEVTDEBUGoutput)

process.schedule = cms.Schedule(process.generation_step,process.simulation_step,
process.digitisation_step,process.digi2raw_step,
process.endjob_step,process.FEVTDEBUGoutput_step)
process.RandomNumberGeneratorService.simMuonGEMDigis = process.RandomNumberGeneratorService.generator