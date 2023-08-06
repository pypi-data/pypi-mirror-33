// STL headers
#if __has_include("cstdlib")
#include <cstdlib>
#endif
#if __has_include("csignal")
#include <csignal>
#endif
#if __has_include("csetjmp")
#include <csetjmp>
#endif
#if __has_include("cstdarg")
#include <cstdarg>
#endif
#if __has_include("typeinfo")
#include <typeinfo>
#endif
#if __has_include("typeindex")
#include <typeindex>
#endif
#if __has_include("type_traits")
#include <type_traits>
#endif
#if __has_include("bitset")
#include <bitset>
#endif
#if __has_include("functional")
#include <functional>
#endif
#if __has_include("utility")
#include <utility>
#endif
#if __has_include("ctime")
#include <ctime>
#endif
#if __has_include("chrono")
#include <chrono>
#endif
#if __has_include("cstddef")
#include <cstddef>
#endif
#if __has_include("initializer_list")
#include <initializer_list>
#endif
#if __has_include("tuple")
#include <tuple>
#endif
#if __has_include("new")
#include <new>
#endif
#if __has_include("memory")
#include <memory>
#endif
#if __has_include("scoped_allocator")
#include <scoped_allocator>
#endif
#if __has_include("climits")
#include <climits>
#endif
#if __has_include("cfloat")
#include <cfloat>
#endif
#if __has_include("cstdint")
#include <cstdint>
#endif
#if __has_include("cinttypes")
#include <cinttypes>
#endif
#if __has_include("limits")
#include <limits>
#endif
#if __has_include("exception")
#include <exception>
#endif
#if __has_include("stdexcept")
#include <stdexcept>
#endif
#if __has_include("cassert")
#include <cassert>
#endif
#if __has_include("system_error")
#include <system_error>
#endif
#if __has_include("cerrno")
#include <cerrno>
#endif
#if __has_include("cctype")
#include <cctype>
#endif
#if __has_include("cwctype")
#include <cwctype>
#endif
#if __has_include("cstring")
#include <cstring>
#endif
#if __has_include("cwchar")
#include <cwchar>
#endif
#if __has_include("cuchar")
#include <cuchar>
#endif
#if __has_include("string")
#include <string>
#endif
#if __has_include("array")
#include <array>
#endif
#if __has_include("vector")
#include <vector>
#endif
#if __has_include("deque")
#include <deque>
#endif
#if __has_include("list")
#include <list>
#endif
#if __has_include("forward_list")
#include <forward_list>
#endif
#if __has_include("set")
#include <set>
#endif
#if __has_include("map")
#include <map>
#endif
#if __has_include("unordered_set")
#include <unordered_set>
#endif
#if __has_include("unordered_map")
#include <unordered_map>
#endif
#if __has_include("stack")
#include <stack>
#endif
#if __has_include("queue")
#include <queue>
#endif
#if __has_include("algorithm")
#include <algorithm>
#endif
#if __has_include("iterator")
#include <iterator>
#endif
#if __has_include("cmath")
#include <cmath>
#endif
#if __has_include("complex")
#include <complex>
#endif
#if __has_include("valarray")
#include <valarray>
#endif
#if __has_include("random")
#include <random>
#endif
#if __has_include("numeric")
#include <numeric>
#endif
#if __has_include("ratio")
#include <ratio>
#endif
#if __has_include("cfenv")
#include <cfenv>
#endif
#if __has_include("iosfwd")
#include <iosfwd>
#endif
#if __has_include("ios")
#include <ios>
#endif
#if __has_include("istream")
#include <istream>
#endif
#if __has_include("ostream")
#include <ostream>
#endif
#if __has_include("iostream")
#include <iostream>
#endif
#if __has_include("fstream")
#include <fstream>
#endif
#if __has_include("sstream")
#include <sstream>
#endif
#if __has_include("iomanip")
#include <iomanip>
#endif
#if __has_include("streambuf")
#include <streambuf>
#endif
#if __has_include("cstdio")
#include <cstdio>
#endif
#if __has_include("locale")
#include <locale>
#endif
#if __has_include("clocale")
#include <clocale>
#endif
#if __has_include("codecvt")
#include <codecvt>
#endif
#if __has_include("atomic")
#include <atomic>
#endif
#if __has_include("thread")
#include <thread>
#endif
#if __has_include("mutex")
#include <mutex>
#endif
#if __has_include("future")
#include <future>
#endif
#if __has_include("condition_variable")
#include <condition_variable>
#endif
#if __has_include("ciso646")
#include <ciso646>
#endif
#if __has_include("ccomplex")
#include <ccomplex>
#endif
#if __has_include("ctgmath")
#include <ctgmath>
#endif
#if __has_include("cstdalign")
#include <cstdalign>
#endif
#if __has_include("cstdbool")
#include <cstdbool>
#endif
// treat regex separately
#if __has_include("regex") && !defined __APPLE__
#include <regex>
#endif
// STL Deprecated headers
#define _BACKWARD_BACKWARD_WARNING_H
#pragma clang diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated"
#if __has_include("strstream")
#include <strstream>
#endif
#pragma clang diagnostic pop
#undef _BACKWARD_BACKWARD_WARNING_H
#include "etc/cling/Interpreter/DynamicExprInfo.h"
#include "etc/cling/Interpreter/DynamicLookupRuntimeUniverse.h"
#include "etc/cling/Interpreter/DynamicLookupLifetimeHandler.h"
#include "etc/cling/Interpreter/Exception.h"
#include "etc/cling/Interpreter/RuntimePrintValue.h"
#include "etc/cling/Interpreter/RuntimeUniverse.h"
#include "etc/cling/Interpreter/Value.h"
// ./core/clingutils/G__setDict.cxx
#include "set"
// ./core/clingutils/G__vectorDict.cxx
#include "vector"
// ./core/clingutils/G__multimap2Dict.cxx
#include "map"
// ./core/clingutils/G__mapDict.cxx
#include "map"
// ./core/clingutils/G__unordered_multimapDict.cxx
#include "unordered_map"
// ./core/clingutils/G__listDict.cxx
#include "list"
// ./core/clingutils/G__unordered_multisetDict.cxx
#include "unordered_set"
// ./core/clingutils/G__forward_listDict.cxx
#include "forward_list"
// ./core/clingutils/G__unordered_mapDict.cxx
#include "unordered_map"
// ./core/clingutils/G__valarrayDict.cxx
#include "valarray"
// ./core/clingutils/G__multisetDict.cxx
#include "set"
// ./core/clingutils/G__unordered_setDict.cxx
#include "unordered_set"
// ./core/clingutils/G__dequeDict.cxx
#include "deque"
// ./core/clingutils/G__multimapDict.cxx
#include "map"
// ./core/clingutils/G__map2Dict.cxx
#include "map"
// ./core/clingutils/G__complexDict.cxx
#include "root_std_complex.h"
// ./core/thread/G__Thread.cxx
#include "TAtomicCount.h"
#include "TCondition.h"
#include "TConditionImp.h"
#include "TMutex.h"
#include "TMutexImp.h"
#include "TRWLock.h"
#include "ROOT/TRWSpinLock.hxx"
#include "TSemaphore.h"
#include "TThread.h"
#include "TThreadFactory.h"
#include "TThreadImp.h"
#include "ROOT/TThreadedObject.hxx"
#include "TThreadPool.h"
#include "ThreadLocalStorage.h"
#include "ROOT/TSpinMutex.hxx"
#include "ROOT/TReentrantRWLock.hxx"
#include "ROOT/RConcurrentHashColl.hxx"
#include "TPosixCondition.h"
#include "TPosixMutex.h"
#include "TPosixThread.h"
#include "TPosixThreadFactory.h"
#include "PosixThreadInc.h"
// ./core/base/G__Core.cxx
#include "TApplication.h"
#include "TApplicationImp.h"
#include "TAtt3D.h"
#include "TAttAxis.h"
#include "TAttBBox.h"
#include "TAttBBox2D.h"
#include "TAttFill.h"
#include "TAttLine.h"
#include "TAttMarker.h"
#include "TAttPad.h"
#include "TAttText.h"
#include "TBase64.h"
#include "TBenchmark.h"
#include "TBrowser.h"
#include "TBrowserImp.h"
#include "TBuffer.h"
#include "TBuffer3D.h"
#include "TBuffer3DTypes.h"
#include "TCanvasImp.h"
#include "TColor.h"
#include "TColorGradient.h"
#include "TContextMenu.h"
#include "TContextMenuImp.h"
#include "TControlBarImp.h"
#include "TDatime.h"
#include "TDirectory.h"
#include "TEnv.h"
#include "TError.h"
#include "TException.h"
#include "TExec.h"
#include "TFileCollection.h"
#include "TFileInfo.h"
#include "TFolder.h"
#include "TGuiFactory.h"
#include "TInetAddress.h"
#include "TInspectorImp.h"
#include "TMD5.h"
#include "TMacro.h"
#include "TMathBase.h"
#include "TMemberInspector.h"
#include "TMessageHandler.h"
#include "TNamed.h"
#include "TObjString.h"
#include "TObject.h"
#include "TObjectSpy.h"
#include "TPRegexp.h"
#include "TParameter.h"
#include "TPluginManager.h"
#include "TPoint.h"
#include "TProcessID.h"
#include "TProcessUUID.h"
#include "TQClass.h"
#include "TQCommand.h"
#include "TQConnection.h"
#include "TQObject.h"
#include "TROOT.h"
#include "TRedirectOutputGuard.h"
#include "TRef.h"
#include "TRefCnt.h"
#include "TRegexp.h"
#include "TRemoteObject.h"
#include "TRootIOCtor.h"
#include "TStopwatch.h"
#include "TStorage.h"
#include "TString.h"
#include "TStringLong.h"
#include "TStyle.h"
#include "TSysEvtHandler.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TSystemFile.h"
#include "TTask.h"
#include "TThreadSlots.h"
#include "TTime.h"
#include "TTimeStamp.h"
#include "TTimer.h"
#include "TUUID.h"
#include "TUri.h"
#include "TUrl.h"
#include "TVersionCheck.h"
#include "TVirtualAuth.h"
#include "TVirtualFFT.h"
#include "TVirtualMonitoring.h"
#include "TVirtualMutex.h"
#include "TVirtualPS.h"
#include "TVirtualPad.h"
#include "TVirtualPadEditor.h"
#include "TVirtualPadPainter.h"
#include "TVirtualPerfStats.h"
#include "TVirtualQConnection.h"
#include "TVirtualRWMutex.h"
#include "TVirtualTableInterface.h"
#include "TVirtualViewer3D.h"
#include "TVirtualX.h"
#include "Rtypes.h"
#include "GuiTypes.h"
#include "MessageTypes.h"
#include "KeySymbols.h"
#include "Buttons.h"
#include "ROOT/TSequentialExecutor.hxx"
#include "strlcpy.h"
#include "snprintf.h"
#include "TArray.h"
#include "TArrayC.h"
#include "TArrayD.h"
#include "TArrayF.h"
#include "TArrayI.h"
#include "TArrayL.h"
#include "TArrayL64.h"
#include "TArrayS.h"
#include "TBits.h"
#include "TBtree.h"
#include "TClassTable.h"
#include "TClonesArray.h"
#include "TCollection.h"
#include "TCollectionProxyInfo.h"
#include "TExMap.h"
#include "THashList.h"
#include "THashTable.h"
#include "TIterator.h"
#include "TList.h"
#include "TMap.h"
#include "TObjArray.h"
#include "TObjectTable.h"
#include "TOrdCollection.h"
#include "TRefArray.h"
#include "TRefTable.h"
#include "TSeqCollection.h"
#include "TSortedList.h"
#include "TVirtualCollectionProxy.h"
#include "ROOT/TSeq.hxx"
#include "ESTLType.h"
#include "RStringView.h"
#include "TClassEdit.h"
#include "ROOT/RIntegerSequence.hxx"
#include "ROOT/RMakeUnique.hxx"
#include "ROOT/RNotFn.hxx"
#include "ROOT/RSpan.hxx"
#include "ROOT/RStringView.hxx"
#include "ROOT/TypeTraits.hxx"
#include "ROOT/span.hxx"
#include "TUnixSystem.h"
#include "TClingRuntime.h"
#include "root_std_complex.h"
#include "TBaseClass.h"
#include "TClass.h"
#include "TClassGenerator.h"
#include "TClassMenuItem.h"
#include "TClassRef.h"
#include "TClassStreamer.h"
#include "TDataMember.h"
#include "TDataType.h"
#include "TDictAttributeMap.h"
#include "TDictionary.h"
#include "TEnum.h"
#include "TEnumConstant.h"
#include "TFileMergeInfo.h"
#include "TFunction.h"
#include "TFunctionTemplate.h"
#include "TGenericClassInfo.h"
#include "TGlobal.h"
#include "TInterpreter.h"
#include "TInterpreterValue.h"
#include "TIsAProxy.h"
#include "TListOfDataMembers.h"
#include "TListOfEnums.h"
#include "TListOfEnumsWithLock.h"
#include "TListOfFunctionTemplates.h"
#include "TListOfFunctions.h"
#include "TMemberStreamer.h"
#include "TMethod.h"
#include "TMethodArg.h"
#include "TMethodCall.h"
#include "TProtoClass.h"
#include "TRealData.h"
#include "TSchemaHelper.h"
#include "TSchemaRule.h"
#include "TSchemaRuleSet.h"
#include "TStatusBitsChecker.h"
#include "TStreamer.h"
#include "TStreamerElement.h"
#include "TToggle.h"
#include "TToggleGroup.h"
#include "TVirtualIsAProxy.h"
#include "TVirtualRefProxy.h"
#include "TVirtualStreamerInfo.h"
#include "Getline.h"
// ./io/io/G__RIO.cxx
#include "TArchiveFile.h"
#include "TBufferFile.h"
#include "TBufferIO.h"
#include "TBufferJSON.h"
#include "TBufferText.h"
#include "TCollectionProxyFactory.h"
#include "TContainerConverters.h"
#include "TDirectoryFile.h"
#include "TEmulatedCollectionProxy.h"
#include "TEmulatedMapProxy.h"
#include "TFPBlock.h"
#include "TFile.h"
#include "TFileCacheRead.h"
#include "TFileCacheWrite.h"
#include "TFileMerger.h"
#include "TFilePrefetch.h"
#include "TFree.h"
#include "TGenCollectionProxy.h"
#include "TGenCollectionStreamer.h"
#include "TKey.h"
#include "TKeyMapFile.h"
#include "TLockFile.h"
#include "TMakeProject.h"
#include "TMapFile.h"
#include "TMemFile.h"
#include "TStreamerInfo.h"
#include "TStreamerInfoActions.h"
#include "TVirtualArray.h"
#include "TVirtualCollectionIterators.h"
#include "TVirtualObject.h"
#include "TZIPFile.h"
#include "ROOT/TBufferMerger.hxx"
// ./math/mathcore/G__MathCore.cxx
#include "TComplex.h"
#include "TMath.h"
#include "TRandom.h"
#include "TRandom1.h"
#include "TRandom2.h"
#include "TRandom3.h"
#include "TKDTree.h"
#include "TKDTreeBinning.h"
#include "TStatistic.h"
#include "Math/Error.h"
#include "Math/IParamFunction.h"
#include "Math/IFunction.h"
#include "Math/ParamFunctor.h"
#include "Math/Functor.h"
#include "Math/Minimizer.h"
#include "Math/MinimizerOptions.h"
#include "Math/IntegratorOptions.h"
#include "Math/IOptions.h"
#include "Math/GenAlgoOptions.h"
#include "Math/BasicMinimizer.h"
#include "Math/MinimTransformFunction.h"
#include "Math/MinimTransformVariable.h"
#include "Math/Integrator.h"
#include "Math/VirtualIntegrator.h"
#include "Math/AllIntegrationTypes.h"
#include "Math/AdaptiveIntegratorMultiDim.h"
#include "Math/IntegratorMultiDim.h"
#include "Math/Factory.h"
#include "Math/FitMethodFunction.h"
#include "Math/GaussIntegrator.h"
#include "Math/GaussLegendreIntegrator.h"
#include "Math/RootFinder.h"
#include "Math/IRootFinderMethod.h"
#include "Math/RichardsonDerivator.h"
#include "Math/BrentMethods.h"
#include "Math/BrentMinimizer1D.h"
#include "Math/BrentRootFinder.h"
#include "Math/DistSampler.h"
#include "Math/DistSamplerOptions.h"
#include "Math/GoFTest.h"
#include "Math/SpecFuncMathCore.h"
#include "Math/DistFuncMathCore.h"
#include "Math/ChebyshevPol.h"
#include "Math/KDTree.h"
#include "Math/TDataPoint.h"
#include "Math/TDataPointN.h"
#include "Math/Delaunay2D.h"
#include "Math/Random.h"
#include "Math/TRandomEngine.h"
#include "Math/RandomFunctions.h"
#include "Math/StdEngine.h"
#include "Math/MersenneTwisterEngine.h"
#include "Math/MixMaxEngine.h"
#include "TRandomGen.h"
#include "Math/LCGEngine.h"
#include "Math/Types.h"
#include "Fit/BasicFCN.h"
#include "Fit/BinData.h"
#include "Fit/Chi2FCN.h"
#include "Fit/DataOptions.h"
#include "Fit/DataRange.h"
#include "Fit/FcnAdapter.h"
#include "Fit/FitConfig.h"
#include "Fit/FitData.h"
#include "Fit/FitExecutionPolicy.h"
#include "Fit/FitResult.h"
#include "Fit/FitUtil.h"
#include "Fit/Fitter.h"
#include "Fit/LogLikelihoodFCN.h"
#include "Fit/ParameterSettings.h"
#include "Fit/PoissonLikelihoodFCN.h"
#include "Fit/SparseData.h"
#include "Fit/UnBinData.h"
// Extra headers
#include "ROOT/TSeq.hxx"
#include "ROOT/StringConv.hxx"
