WW analysis 2018
====

Setup:

    source setup.sh
    source ../../../latinoRDF/setup.sh

Histogram production


Prepare the scripts:

    mkShapes.py  --pycfg=configuration.py

NB: the preparation of the scripts will clean all the compiled code.

Compile the scripts locally:

    mkShapes.py  --pycfg=configuration.py     --localCompile

Compile the scripts on cluster:

    mkShapes.py  --pycfg=configuration.py     --parallelCompile

Submit on batch system:

    mkShapes.py  --pycfg=configuration.py --submitBatch
    mkShapes.py  --pycfg=configuration.py --submit

Check if done:

    mkShapes.py  --pycfg=configuration.py --checkBatch

Hadd the root files:

    mkShapes.py  --pycfg=configuration.py --hadd


Plot:

    mkPlot.py  --pycfg=configuration.py
    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1

    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1 --skipMissingNuisance

    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1 --skipMissingNuisance   --plotNormalizedDistributions
    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1 --skipMissingNuisance   --plotNormalizedDistributions  --silentMode




Datacards:

    mkDatacards.py  --pycfg=configuration.py

Dump the trees:

    mkSnapshot.py   --pycfg=configuration.py
    mkSnapshot.py   --pycfg=configuration.py  --submitBatch
    mkSnapshot.py   --pycfg=configuration.py  --checkBatch


FIXME:

    use of Redefine vs Define
    and SafeDefine



Readable:

    easyDescription.py --inputFileSamples      samples.py     --outputFileSamples      extended_samples.py
    easyDescription.py --inputFileCuts         cuts.py        --outputFileCuts         extended_cuts.py
    easyDescription.py --inputFileNuisances    nuisances.py   --outputFileNuisances    extended_nuisances.py   --inputFileSamples      samples.py




    g++ -O2 -Wall -pthread -std=c++17 -m64 -fsized-deallocation -I/usr/include/root  my_run_analysis_WpWp_QCD_WpWpJJ_QCD_UL_3.cpp -o my_run_analysis_WpWp_QCD_WpWpJJ_QCD_UL_3 -L/usr/lib64/root -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/usr/lib64/root -pthread -lm -ldl -rdynamic


    g++ -O2 -Wall -pthread -std=c++20 -m64 -fsized-deallocation -I/usr/include/root  my_run_analysis_WpWp_QCD_WpWpJJ_QCD_UL_3.cpp -o my_run_analysis_WpWp_QCD_WpWpJJ_QCD_UL_3 -L/usr/lib64/root -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/usr/lib64/root -pthread -lm -ldl -rdynamic


    g++ -O2 -Wall -pthread -std=c++17 -m64 -fsized-deallocation -I/usr/include/root -std=c++20 -Wcpp  scripts_run/WpWp_QCD/WpWpJJ_QCD_UL/my_run_analysis_WpWp_QCD_WpWpJJ_QCD_UL_10.cpp -o scripts_run/WpWp_QCD/WpWpJJ_QCD_UL/my_run_analysis_WpWp_QCD_WpWpJJ_QCD_UL_10 -L/usr/lib64/root -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/usr/lib64/root -pthread -lm -ldl -rdynamic

    g++ -O2 -Wall -pthread -std=c++17 -m64 -fsized-deallocation -I/usr/include/root scripts_run/SSWW/WpWpJJ_EWK_UL/my_run_analysis_SSWW_WpWpJJ_EWK_UL_24.cpp -o scripts_run/SSWW/WpWpJJ_EWK_UL/my_run_analysis_SSWW_WpWpJJ_EWK_UL_24 -L/usr/lib64/root -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/usr/lib64/root -pthread -lm -ldl -rdynamic


    g++ -O2 -Wall -pthread -std=c++17 -m64 -fsized-deallocation -I/usr/include/root  scripts_run/SSWW/WpWpJJ_EWK_UL/my_run_analysis_SSWW_WpWpJJ_EWK_UL_3.cpp -o ./scripts_run/SSWW/WpWpJJ_EWK_UL/my_run_analysis_SSWW_WpWpJJ_EWK_UL_3 -L/usr/lib64/root -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/usr/lib64/root -pthread -lm -ldl -rdynamic


    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10.cpp -o scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -Wl,-rpath,'$ORIGIN:$ORIGINscripts_run/'

    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10.cpp -o scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame \
    -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include \
    -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib \
    -lcorrectionlib \
    -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -Wl,-rpath,'$ORIGIN:$ORIGINscripts_run/'



    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10.cpp -o scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame \
    -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include \
    -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib \
    -lcorrectionlib \
    -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -Wl,-rpath,'$ORIGIN:$ORIGINscripts_run/'




    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10.cpp -o scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame \
    -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include \
    -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib \
    -lcorrectionlib \
    -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -Wl,-rpath,'$ORIGIN:/afs/cern.ch/user/a/amassiro/work/Latinos/Framework/RDF/plotsConfigurationsRDF/WW/2018/scripts_run/'


    scripts_run/DY/DYJetsToLL_M-50/my_run_analysis_DY_DYJetsToLL_M-50_10


    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/DY/DYJetsToLL_M-10to50_NLO/my_run_analysis_DY_DYJetsToLL_M-10to50_NLO_0.cpp -o scripts_run/DY/DYJetsToLL_M-10to50_NLO/my_run_analysis_DY_DYJetsToLL_M-10to50_NLO_0 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib -lcorrectionlib -Wl, -rpath,'$ORIGIN:$ORIGINscripts_run/'


    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/DY/DYJetsToLL_M-10to50_NLO/my_run_analysis_DY_DYJetsToLL_M-10to50_NLO_0.cpp -o scripts_run/DY/DYJetsToLL_M-10to50_NLO/my_run_analysis_DY_DYJetsToLL_M-10to50_NLO_0 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -Wl,-rpath,'$ORIGIN:$ORIGINscripts_run/'



    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/top/TTTo2L2Nu/my_run_analysis_top_TTTo2L2Nu_0.cpp -o scripts_run/top/TTTo2L2Nu/my_run_analysis_top_TTTo2L2Nu_0 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib -lcorrectionlib -Wl,-rpath,'$ORIGIN:$ORIGINscripts_run/'


    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include -Iscripts_run/  scripts_run/top/TTTo2L2Nu/my_run_analysis_top_TTTo2L2Nu_0.cpp -o scripts_run/top/TTTo2L2Nu/my_run_analysis_top_TTTo2L2Nu_0 -Lscripts_run/ -llibrary_utils -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib -lcorrectionlib -Wl,-rpath,'$ORIGIN:$ORIGIN/../../'



    g++ -O2 -Wall -fPIC -pthread -std=c++20 -m64 -fsized-deallocation \
    -I/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/include \
    -Iscripts_run/ scripts_run/top/TTTo2L2Nu/my_run_analysis_top_TTTo2L2Nu_0.cpp \
    -o scripts_run/top/TTTo2L2Nu/my_run_analysis_top_TTTo2L2Nu_0 \
    -Lscripts_run/ -llibrary_utils \
    -L/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib \
    -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame \
    -Wl,-rpath,/cvmfs/sft.cern.ch/lcg/releases/ROOT/6.38.04-57e03/x86_64-el9-gcc13-opt/lib \
    -pthread -lm -ldl -rdynamic -lTMVA -lXMLIO \
    -I/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/include \
    -L/cvmfs/sft.cern.ch/lcg/views/LCG_109a/x86_64-el9-gcc13-opt/lib \
    -lcorrectionlib \
    -Wl,-rpath,'$ORIGIN/../../'





    rpath_flags = "-Wl,-rpath,'$$ORIGIN:$$ORIGIN/../..'"




