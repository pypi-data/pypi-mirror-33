#define BOOST_SIMD_NO_STRICT_ALIASING 1
#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/include/types/numpy_texpr.hpp>
#include <pythonic/include/types/int.hpp>
#include <pythonic/include/types/complex128.hpp>
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/uint8.hpp>
#include <pythonic/types/complex128.hpp>
#include <pythonic/types/numpy_texpr.hpp>
#include <pythonic/types/int.hpp>
#include <pythonic/types/uint8.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/include/operator_/div.hpp>
#include <pythonic/include/__builtin__/getattr.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/include/operator_/idiv.hpp>
#include <pythonic/include/__builtin__/tuple.hpp>
#include <pythonic/include/numpy/empty_like.hpp>
#include <pythonic/include/numpy/square.hpp>
#include <pythonic/include/types/complex.hpp>
#include <pythonic/include/__builtin__/range.hpp>
#include <pythonic/include/__builtin__/None.hpp>
#include <pythonic/operator_/div.hpp>
#include <pythonic/__builtin__/getattr.hpp>
#include <pythonic/types/str.hpp>
#include <pythonic/operator_/idiv.hpp>
#include <pythonic/__builtin__/tuple.hpp>
#include <pythonic/numpy/empty_like.hpp>
#include <pythonic/numpy/square.hpp>
#include <pythonic/types/complex.hpp>
#include <pythonic/__builtin__/range.hpp>
#include <pythonic/__builtin__/None.hpp>
namespace __pythran_util_pythran
{
  struct myfunc
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::square{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type1;
      typedef decltype(std::declval<__type0>()(std::declval<__type1>())) __type2;
      typedef decltype((std::declval<__type2>() * std::declval<__type1>())) __type3;
      typedef decltype((std::declval<__type2>() + std::declval<__type3>())) __type4;
      typedef long __type5;
      typedef decltype((std::declval<__type4>() + std::declval<__type5>())) __type6;
      typedef double __type7;
      typedef typename pythonic::returnable<decltype((pythonic::operator_::div(std::declval<__type6>(), std::declval<__type7>())))>::type result_type;
    }  
    ;
    template <typename argument_type0 >
    typename type<argument_type0>::result_type operator()(argument_type0&& a) const
    ;
  }  ;
  struct rotfft_from_vecfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    struct type
    {
      typedef std::complex<double> __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type2;
      typedef decltype((std::declval<__type1>() * std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type5;
      typedef decltype((std::declval<__type4>() * std::declval<__type5>())) __type6;
      typedef decltype((std::declval<__type3>() - std::declval<__type6>())) __type7;
      typedef typename pythonic::returnable<decltype((std::declval<__type0>() * std::declval<__type7>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type operator()(argument_type0&& vecx_fft, argument_type1&& vecy_fft, argument_type2&& KX, argument_type3&& KY) const
    ;
  }  ;
  struct divfft_from_vecfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    struct type
    {
      typedef std::complex<double> __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype((std::declval<__type1>() * std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type5;
      typedef decltype((std::declval<__type4>() * std::declval<__type5>())) __type6;
      typedef decltype((std::declval<__type3>() + std::declval<__type6>())) __type7;
      typedef typename pythonic::returnable<decltype((std::declval<__type0>() * std::declval<__type7>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type operator()(argument_type0&& vecx_fft, argument_type1&& vecy_fft, argument_type2&& KX, argument_type3&& KY) const
    ;
  }  ;
  struct gradfft_from_fft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type0>())) __type2;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type2>::type>::type __type3;
      typedef typename pythonic::lazy<__type3>::type __type4;
      typedef decltype(std::declval<__type1>()(std::declval<__type4>())) __type5;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type5>::type::iterator>::value_type>::type __type6;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type2>::type>::type __type7;
      typedef typename pythonic::lazy<__type7>::type __type8;
      typedef decltype(std::declval<__type1>()(std::declval<__type8>())) __type9;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type9>::type::iterator>::value_type>::type __type10;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type6>(), std::declval<__type10>())) __type11;
      typedef decltype(std::declval<__type0>()[std::declval<__type11>()]) __type12;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::empty_like{})>::type>::type __type13;
      typedef typename pythonic::assignable<decltype(std::declval<__type13>()(std::declval<__type0>()))>::type __type14;
      typedef indexable<__type11> __type15;
      typedef typename __combined<__type14,__type15>::type __type16;
      typedef std::complex<double> __type17;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type18;
      typedef decltype(std::declval<__type18>()[std::declval<__type11>()]) __type19;
      typedef decltype((std::declval<__type17>() * std::declval<__type19>())) __type20;
      typedef typename pythonic::assignable<decltype(std::declval<__type0>()[std::declval<__type11>()])>::type __type21;
      typedef decltype((std::declval<__type20>() * std::declval<__type21>())) __type22;
      typedef container<typename std::remove_reference<__type22>::type> __type23;
      typedef typename __combined<__type16,__type23>::type __type24;
      typedef typename __combined<__type24,__type15>::type __type25;
      typedef typename __combined<__type25,__type23>::type __type26;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type27;
      typedef decltype(std::declval<__type27>()[std::declval<__type11>()]) __type28;
      typedef decltype((std::declval<__type17>() * std::declval<__type28>())) __type29;
      typedef decltype((std::declval<__type29>() * std::declval<__type21>())) __type30;
      typedef container<typename std::remove_reference<__type30>::type> __type31;
      typedef typename __combined<__type16,__type31>::type __type32;
      typedef typename __combined<__type32,__type15>::type __type33;
      typedef typename __combined<__type33,__type31>::type __type34;
      typedef __type12 __ptype0;
      typedef typename pythonic::returnable<decltype(pythonic::types::make_tuple(std::declval<__type26>(), std::declval<__type34>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0&& f_fft, argument_type1&& KX, argument_type2&& KY) const
    ;
  }  ;
  struct vecfft_from_divfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    struct type
    {
      typedef std::complex<double> __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type1;
      typedef decltype((std::declval<__type0>() * std::declval<__type1>())) __type2;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type3;
      typedef decltype((std::declval<__type2>() * std::declval<__type3>())) __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type5;
      typedef decltype((std::declval<__type0>() * std::declval<__type5>())) __type6;
      typedef decltype((std::declval<__type6>() * std::declval<__type3>())) __type7;
      typedef typename pythonic::returnable<decltype(pythonic::types::make_tuple(std::declval<__type4>(), std::declval<__type7>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0&& div_fft, argument_type1&& KX_over_K2, argument_type2&& KY_over_K2) const
    ;
  }  ;
  struct vecfft_from_rotfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    struct type
    {
      typedef std::complex<double> __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type1;
      typedef decltype((std::declval<__type0>() * std::declval<__type1>())) __type2;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type3;
      typedef decltype((std::declval<__type2>() * std::declval<__type3>())) __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type5;
      typedef decltype((std::declval<__type0>() * std::declval<__type5>())) __type6;
      typedef decltype((std::declval<__type6>() * std::declval<__type3>())) __type7;
      typedef typename pythonic::returnable<decltype(pythonic::types::make_tuple(std::declval<__type4>(), std::declval<__type7>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0&& rot_fft, argument_type1&& KX_over_K2, argument_type2&& KY_over_K2) const
    ;
  }  ;
  struct dealiasing_variable
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    struct type
    {
      typedef double __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type2;
      typedef decltype(std::declval<__type1>()(std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type3>::type::iterator>::value_type>::type __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type5>())) __type6;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type6>::type::iterator>::value_type>::type __type7;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type4>(), std::declval<__type7>())) __type8;
      typedef __type0 __ptype1;
      typedef __type8 __ptype2;
      typedef typename pythonic::returnable<pythonic::types::none_type>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type operator()(argument_type0&& ff_fft, argument_type1&& where, argument_type2&& nK0loc, argument_type3&& nK1loc) const
    ;
  }  ;
  template <typename argument_type0 >
  typename myfunc::type<argument_type0>::result_type myfunc::operator()(argument_type0&& a) const
  {
    return (pythonic::operator_::div(((pythonic::numpy::functor::square{}(a) + (pythonic::numpy::functor::square{}(a) * a)) + 2L), 5.0));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
  typename rotfft_from_vecfft::type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type rotfft_from_vecfft::operator()(argument_type0&& vecx_fft, argument_type1&& vecy_fft, argument_type2&& KX, argument_type3&& KY) const
  {
    return (std::complex<double>(0.0, 1.0) * ((KX * vecy_fft) - (KY * vecx_fft)));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
  typename divfft_from_vecfft::type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type divfft_from_vecfft::operator()(argument_type0&& vecx_fft, argument_type1&& vecy_fft, argument_type2&& KX, argument_type3&& KY) const
  {
    return (std::complex<double>(0.0, 1.0) * ((KX * vecx_fft) + (KY * vecy_fft)));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
  typename gradfft_from_fft::type<argument_type0, argument_type1, argument_type2>::result_type gradfft_from_fft::operator()(argument_type0&& f_fft, argument_type1&& KX, argument_type2&& KY) const
  {
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::empty_like{})>::type>::type __type0;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type1;
    typedef typename pythonic::assignable<decltype(std::declval<__type0>()(std::declval<__type1>()))>::type __type2;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type3;
    typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type1>())) __type4;
    typedef typename std::tuple_element<0,typename std::remove_reference<__type4>::type>::type __type5;
    typedef typename pythonic::lazy<__type5>::type __type6;
    typedef decltype(std::declval<__type3>()(std::declval<__type6>())) __type7;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type7>::type::iterator>::value_type>::type __type8;
    typedef typename std::tuple_element<1,typename std::remove_reference<__type4>::type>::type __type9;
    typedef typename pythonic::lazy<__type9>::type __type10;
    typedef decltype(std::declval<__type3>()(std::declval<__type10>())) __type11;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type11>::type::iterator>::value_type>::type __type12;
    typedef decltype(pythonic::types::make_tuple(std::declval<__type8>(), std::declval<__type12>())) __type13;
    typedef indexable<__type13> __type14;
    typedef typename __combined<__type2,__type14>::type __type15;
    typedef std::complex<double> __type16;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type17;
    typedef decltype(std::declval<__type17>()[std::declval<__type13>()]) __type18;
    typedef decltype((std::declval<__type16>() * std::declval<__type18>())) __type19;
    typedef typename pythonic::assignable<decltype(std::declval<__type1>()[std::declval<__type13>()])>::type __type20;
    typedef decltype((std::declval<__type19>() * std::declval<__type20>())) __type21;
    typedef container<typename std::remove_reference<__type21>::type> __type22;
    typedef typename __combined<__type15,__type22>::type __type23;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type24;
    typedef decltype(std::declval<__type24>()[std::declval<__type13>()]) __type25;
    typedef decltype((std::declval<__type16>() * std::declval<__type25>())) __type26;
    typedef decltype((std::declval<__type26>() * std::declval<__type20>())) __type27;
    typedef container<typename std::remove_reference<__type27>::type> __type28;
    typedef typename __combined<__type15,__type28>::type __type29;
    typename pythonic::assignable<typename __combined<__type23,__type14>::type>::type px_f_fft = pythonic::numpy::functor::empty_like{}(f_fft);
    typename pythonic::assignable<typename __combined<__type29,__type14>::type>::type py_f_fft = pythonic::numpy::functor::empty_like{}(f_fft);
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(f_fft)))>::type n0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(f_fft));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(f_fft)))>::type n1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(f_fft));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            typename pythonic::assignable<decltype(f_fft.fast(pythonic::types::make_tuple(i0, i1)))>::type field = f_fft.fast(pythonic::types::make_tuple(i0, i1));
            px_f_fft.fast(pythonic::types::make_tuple(i0, i1)) = ((std::complex<double>(0.0, 1.0) * KX.fast(pythonic::types::make_tuple(i0, i1))) * field);
            py_f_fft.fast(pythonic::types::make_tuple(i0, i1)) = ((std::complex<double>(0.0, 1.0) * KY.fast(pythonic::types::make_tuple(i0, i1))) * field);
          }
        }
      }
    }
    return pythonic::types::make_tuple(px_f_fft, py_f_fft);
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
  typename vecfft_from_divfft::type<argument_type0, argument_type1, argument_type2>::result_type vecfft_from_divfft::operator()(argument_type0&& div_fft, argument_type1&& KX_over_K2, argument_type2&& KY_over_K2) const
  {
    ;
    ;
    return pythonic::types::make_tuple(((std::complex<double>(-0.0, -1.0) * KX_over_K2) * div_fft), ((std::complex<double>(-0.0, -1.0) * KY_over_K2) * div_fft));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
  typename vecfft_from_rotfft::type<argument_type0, argument_type1, argument_type2>::result_type vecfft_from_rotfft::operator()(argument_type0&& rot_fft, argument_type1&& KX_over_K2, argument_type2&& KY_over_K2) const
  {
    ;
    ;
    return pythonic::types::make_tuple(((std::complex<double>(0.0, 1.0) * KY_over_K2) * rot_fft), ((std::complex<double>(-0.0, -1.0) * KX_over_K2) * rot_fft));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
  typename dealiasing_variable::type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type dealiasing_variable::operator()(argument_type0&& ff_fft, argument_type1&& where, argument_type2&& nK0loc, argument_type3&& nK1loc) const
  {
    {
      long  __target1 = nK0loc;
      for (long  iK0=0L; iK0 < __target1; iK0 += 1L)
      {
        {
          long  __target2 = nK1loc;
          for (long  iK1=0L; iK1 < __target2; iK1 += 1L)
          {
            if (where.fast(pythonic::types::make_tuple(iK0, iK1)))
            {
              ff_fft.fast(pythonic::types::make_tuple(iK0, iK1)) = 0.0;
            }
          }
        }
      }
    }
    return pythonic::__builtin__::None;
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
typename __pythran_util_pythran::myfunc::type<pythonic::types::ndarray<std::complex<double>,2>>::result_type myfunc0(pythonic::types::ndarray<std::complex<double>,2>&& a) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::myfunc()(a);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::myfunc::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>::result_type myfunc1(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& a) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::myfunc()(a);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::myfunc::type<pythonic::types::ndarray<double,2>>::result_type myfunc2(pythonic::types::ndarray<double,2>&& a) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::myfunc()(a);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::myfunc::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type myfunc3(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& a) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::myfunc()(a);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft0(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft1(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft2(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft3(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft4(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft5(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft6(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft7(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft8(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft9(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft10(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft11(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft12(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft13(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type rotfft_from_vecfft14(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type rotfft_from_vecfft15(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft0(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft1(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft2(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft3(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft4(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft5(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft6(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft7(pythonic::types::ndarray<std::complex<double>,2>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft8(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft9(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft10(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft11(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::ndarray<std::complex<double>,2>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft12(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft13(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type divfft_from_vecfft14(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type divfft_from_vecfft15(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecx_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& vecy_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vecx_fft, vecy_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type gradfft_from_fft0(pythonic::types::ndarray<std::complex<double>,2>&& f_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type gradfft_from_fft1(pythonic::types::ndarray<std::complex<double>,2>&& f_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type gradfft_from_fft2(pythonic::types::ndarray<std::complex<double>,2>&& f_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type gradfft_from_fft3(pythonic::types::ndarray<std::complex<double>,2>&& f_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type gradfft_from_fft4(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& f_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type gradfft_from_fft5(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& f_fft, pythonic::types::ndarray<double,2>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type gradfft_from_fft6(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& f_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::ndarray<double,2>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::gradfft_from_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type gradfft_from_fft7(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& f_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::gradfft_from_fft()(f_fft, KX, KY);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_divfft0(pythonic::types::ndarray<std::complex<double>,2>&& div_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_divfft1(pythonic::types::ndarray<std::complex<double>,2>&& div_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_divfft2(pythonic::types::ndarray<std::complex<double>,2>&& div_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_divfft3(pythonic::types::ndarray<std::complex<double>,2>&& div_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_divfft4(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& div_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_divfft5(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& div_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_divfft6(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& div_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_divfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_divfft7(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& div_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_divfft()(div_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_rotfft0(pythonic::types::ndarray<std::complex<double>,2>&& rot_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_rotfft1(pythonic::types::ndarray<std::complex<double>,2>&& rot_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_rotfft2(pythonic::types::ndarray<std::complex<double>,2>&& rot_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_rotfft3(pythonic::types::ndarray<std::complex<double>,2>&& rot_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_rotfft4(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& rot_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<double,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_rotfft5(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& rot_fft, pythonic::types::ndarray<double,2>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::ndarray<double,2>>::result_type vecfft_from_rotfft6(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& rot_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::ndarray<double,2>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vecfft_from_rotfft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>::result_type vecfft_from_rotfft7(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& rot_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KX_over_K2, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>&& KY_over_K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vecfft_from_rotfft()(rot_fft, KX_over_K2, KY_over_K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::dealiasing_variable::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::ndarray<uint8_t,2>, long, long>::result_type dealiasing_variable0(pythonic::types::ndarray<std::complex<double>,2>&& ff_fft, pythonic::types::ndarray<uint8_t,2>&& where, long&& nK0loc, long&& nK1loc) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::dealiasing_variable()(ff_fft, where, nK0loc, nK1loc);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::dealiasing_variable::type<pythonic::types::ndarray<std::complex<double>,2>, pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>, long, long>::result_type dealiasing_variable1(pythonic::types::ndarray<std::complex<double>,2>&& ff_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>&& where, long&& nK0loc, long&& nK1loc) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::dealiasing_variable()(ff_fft, where, nK0loc, nK1loc);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::dealiasing_variable::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::ndarray<uint8_t,2>, long, long>::result_type dealiasing_variable2(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& ff_fft, pythonic::types::ndarray<uint8_t,2>&& where, long&& nK0loc, long&& nK1loc) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::dealiasing_variable()(ff_fft, where, nK0loc, nK1loc);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::dealiasing_variable::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>, long, long>::result_type dealiasing_variable3(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>&& ff_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>&& where, long&& nK0loc, long&& nK1loc) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::dealiasing_variable()(ff_fft, where, nK0loc, nK1loc);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}

static PyObject *
__pythran_wrap_myfunc0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[1+1];
    char const* keywords[] = {"a", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "O",
                                     (char**)keywords, &args_obj[0]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]))
        return to_python(myfunc0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_myfunc1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[1+1];
    char const* keywords[] = {"a", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "O",
                                     (char**)keywords, &args_obj[0]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]))
        return to_python(myfunc1(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_myfunc2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[1+1];
    char const* keywords[] = {"a", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "O",
                                     (char**)keywords, &args_obj[0]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,2>>(args_obj[0]))
        return to_python(myfunc2(from_python<pythonic::types::ndarray<double,2>>(args_obj[0])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_myfunc3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[1+1];
    char const* keywords[] = {"a", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "O",
                                     (char**)keywords, &args_obj[0]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[0]))
        return to_python(myfunc3(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[0])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft1(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft2(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft3(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft4(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft5(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft6(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft7(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft8(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft8(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft9(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft9(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft10(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft10(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft11(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft11(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft12(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft12(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft13(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft13(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft14(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(rotfft_from_vecfft14(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft15(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(rotfft_from_vecfft15(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft1(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft2(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft3(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft4(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft5(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft6(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft7(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft8(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft8(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft9(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft9(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft10(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft10(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft11(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft11(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft12(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft12(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft13(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft13(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft14(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[3]))
        return to_python(divfft_from_vecfft14(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,2>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft15(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"vecx_fft","vecy_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3]))
        return to_python(divfft_from_vecfft15(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(gradfft_from_fft0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(gradfft_from_fft1(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(gradfft_from_fft2(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(gradfft_from_fft3(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(gradfft_from_fft4(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(gradfft_from_fft5(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(gradfft_from_fft6(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_gradfft_from_fft7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"f_fft","KX","KY", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(gradfft_from_fft7(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_divfft0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_divfft1(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_divfft2(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_divfft3(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_divfft4(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_divfft5(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_divfft6(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_divfft7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"div_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_divfft7(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_rotfft0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_rotfft1(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_rotfft2(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_rotfft3(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_rotfft4(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_rotfft5(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,2>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,2>>(args_obj[2]))
        return to_python(vecfft_from_rotfft6(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,2>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vecfft_from_rotfft7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"rot_fft","KX_over_K2","KY_over_K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2]))
        return to_python(vecfft_from_rotfft7(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,2>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_dealiasing_variable0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"ff_fft","where","nK0loc","nK1loc", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<uint8_t,2>>(args_obj[1]) && is_convertible<long>(args_obj[2]) && is_convertible<long>(args_obj[3]))
        return to_python(dealiasing_variable0(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::ndarray<uint8_t,2>>(args_obj[1]), from_python<long>(args_obj[2]), from_python<long>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_dealiasing_variable1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"ff_fft","where","nK0loc","nK1loc", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>>(args_obj[1]) && is_convertible<long>(args_obj[2]) && is_convertible<long>(args_obj[3]))
        return to_python(dealiasing_variable1(from_python<pythonic::types::ndarray<std::complex<double>,2>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>>(args_obj[1]), from_python<long>(args_obj[2]), from_python<long>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_dealiasing_variable2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"ff_fft","where","nK0loc","nK1loc", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<uint8_t,2>>(args_obj[1]) && is_convertible<long>(args_obj[2]) && is_convertible<long>(args_obj[3]))
        return to_python(dealiasing_variable2(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::ndarray<uint8_t,2>>(args_obj[1]), from_python<long>(args_obj[2]), from_python<long>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_dealiasing_variable3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    char const* keywords[] = {"ff_fft","where","nK0loc","nK1loc", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>>(args_obj[1]) && is_convertible<long>(args_obj[2]) && is_convertible<long>(args_obj[3]))
        return to_python(dealiasing_variable3(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,2>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<uint8_t,2>>>(args_obj[1]), from_python<long>(args_obj[2]), from_python<long>(args_obj[3])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_myfunc(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_myfunc0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_myfunc1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_myfunc2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_myfunc3(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "myfunc", "   myfunc(complex128[][])\n   myfunc(complex128[][].T)\n   myfunc(float64[][])\n   myfunc(float64[][].T)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_rotfft_from_vecfft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft7(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft8(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft9(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft10(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft11(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft12(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft13(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft14(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft15(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "rotfft_from_vecfft", "   rotfft_from_vecfft(complex128[][],complex128[][],float64[][],float64[][])\n   rotfft_from_vecfft(complex128[][],complex128[][],float64[][],float64[][].T)\n   rotfft_from_vecfft(complex128[][],complex128[][],float64[][].T,float64[][])\n   rotfft_from_vecfft(complex128[][],complex128[][],float64[][].T,float64[][].T)\n   rotfft_from_vecfft(complex128[][],complex128[][].T,float64[][],float64[][])\n   rotfft_from_vecfft(complex128[][],complex128[][].T,float64[][],float64[][].T)\n   rotfft_from_vecfft(complex128[][],complex128[][].T,float64[][].T,float64[][])\n   rotfft_from_vecfft(complex128[][],complex128[][].T,float64[][].T,float64[][].T)\n   rotfft_from_vecfft(complex128[][].T,complex128[][],float64[][],float64[][])\n   rotfft_from_vecfft(complex128[][].T,complex128[][],float64[][],float64[][].T)\n   rotfft_from_vecfft(complex128[][].T,complex128[][],float64[][].T,float64[][])\n   rotfft_from_vecfft(complex128[][].T,complex128[][],float64[][].T,float64[][].T)\n   rotfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][],float64[][])\n   rotfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][],float64[][].T)\n   rotfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][].T,float64[][])\n   rotfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][].T,float64[][].T)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_divfft_from_vecfft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_divfft_from_vecfft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft7(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft8(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft9(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft10(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft11(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft12(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft13(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft14(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_divfft_from_vecfft15(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "divfft_from_vecfft", "   divfft_from_vecfft(complex128[][],complex128[][],float64[][],float64[][])\n   divfft_from_vecfft(complex128[][],complex128[][],float64[][],float64[][].T)\n   divfft_from_vecfft(complex128[][],complex128[][],float64[][].T,float64[][])\n   divfft_from_vecfft(complex128[][],complex128[][],float64[][].T,float64[][].T)\n   divfft_from_vecfft(complex128[][],complex128[][].T,float64[][],float64[][])\n   divfft_from_vecfft(complex128[][],complex128[][].T,float64[][],float64[][].T)\n   divfft_from_vecfft(complex128[][],complex128[][].T,float64[][].T,float64[][])\n   divfft_from_vecfft(complex128[][],complex128[][].T,float64[][].T,float64[][].T)\n   divfft_from_vecfft(complex128[][].T,complex128[][],float64[][],float64[][])\n   divfft_from_vecfft(complex128[][].T,complex128[][],float64[][],float64[][].T)\n   divfft_from_vecfft(complex128[][].T,complex128[][],float64[][].T,float64[][])\n   divfft_from_vecfft(complex128[][].T,complex128[][],float64[][].T,float64[][].T)\n   divfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][],float64[][])\n   divfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][],float64[][].T)\n   divfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][].T,float64[][])\n   divfft_from_vecfft(complex128[][].T,complex128[][].T,float64[][].T,float64[][].T)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_gradfft_from_fft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_gradfft_from_fft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_gradfft_from_fft7(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "gradfft_from_fft", "   gradfft_from_fft(complex128[][],float64[][],float64[][])\n   gradfft_from_fft(complex128[][],float64[][],float64[][].T)\n   gradfft_from_fft(complex128[][],float64[][].T,float64[][])\n   gradfft_from_fft(complex128[][],float64[][].T,float64[][].T)\n   gradfft_from_fft(complex128[][].T,float64[][],float64[][])\n   gradfft_from_fft(complex128[][].T,float64[][],float64[][].T)\n   gradfft_from_fft(complex128[][].T,float64[][].T,float64[][])\n   gradfft_from_fft(complex128[][].T,float64[][].T,float64[][].T)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_vecfft_from_divfft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_vecfft_from_divfft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_divfft7(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "vecfft_from_divfft", "   vecfft_from_divfft(complex128[][],float64[][],float64[][])\n   vecfft_from_divfft(complex128[][],float64[][],float64[][].T)\n   vecfft_from_divfft(complex128[][],float64[][].T,float64[][])\n   vecfft_from_divfft(complex128[][],float64[][].T,float64[][].T)\n   vecfft_from_divfft(complex128[][].T,float64[][],float64[][])\n   vecfft_from_divfft(complex128[][].T,float64[][],float64[][].T)\n   vecfft_from_divfft(complex128[][].T,float64[][].T,float64[][])\n   vecfft_from_divfft(complex128[][].T,float64[][].T,float64[][].T)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_vecfft_from_rotfft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_vecfft_from_rotfft7(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "vecfft_from_rotfft", "   vecfft_from_rotfft(complex128[][],float64[][],float64[][])\n   vecfft_from_rotfft(complex128[][],float64[][],float64[][].T)\n   vecfft_from_rotfft(complex128[][],float64[][].T,float64[][])\n   vecfft_from_rotfft(complex128[][],float64[][].T,float64[][].T)\n   vecfft_from_rotfft(complex128[][].T,float64[][],float64[][])\n   vecfft_from_rotfft(complex128[][].T,float64[][],float64[][].T)\n   vecfft_from_rotfft(complex128[][].T,float64[][].T,float64[][])\n   vecfft_from_rotfft(complex128[][].T,float64[][].T,float64[][].T)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_dealiasing_variable(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_dealiasing_variable0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_dealiasing_variable1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_dealiasing_variable2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_dealiasing_variable3(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "dealiasing_variable", "   dealiasing_variable(complex128[][],uint8[][],int,int)\n   dealiasing_variable(complex128[][],uint8[][].T,int,int)\n   dealiasing_variable(complex128[][].T,uint8[][],int,int)\n   dealiasing_variable(complex128[][].T,uint8[][].T,int,int)", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "myfunc",
    (PyCFunction)__pythran_wrapall_myfunc,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n\n    - myfunc(complex128[][])\n    - myfunc(complex128[][].T)\n    - myfunc(float64[][])\n    - myfunc(float64[][].T)"},{
    "rotfft_from_vecfft",
    (PyCFunction)__pythran_wrapall_rotfft_from_vecfft,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n\n    - rotfft_from_vecfft(complex128[][], complex128[][], float64[][], float64[][])\n    - rotfft_from_vecfft(complex128[][], complex128[][], float64[][], float64[][].T)\n    - rotfft_from_vecfft(complex128[][], complex128[][], float64[][].T, float64[][])\n    - rotfft_from_vecfft(complex128[][], complex128[][], float64[][].T, float64[][].T)\n    - rotfft_from_vecfft(complex128[][], complex128[][].T, float64[][], float64[][])\n    - rotfft_from_vecfft(complex128[][], complex128[][].T, float64[][], float64[][].T)\n    - rotfft_from_vecfft(complex128[][], complex128[][].T, float64[][].T, float64[][])\n    - rotfft_from_vecfft(complex128[][], complex128[][].T, float64[][].T, float64[][].T)\n    - rotfft_from_vecfft(complex128[][].T, complex128[][], float64[][], float64[][])\n    - rotfft_from_vecfft(complex128[][].T, complex128[][], float64[][], float64[][].T)\n    - rotfft_from_vecfft(complex128[][].T, complex128[][], float64[][].T, float64[][])\n    - rotfft_from_vecfft(complex128[][].T, complex128[][], float64[][].T, float64[][].T)\n    - rotfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][], float64[][])\n    - rotfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][], float64[][].T)\n    - rotfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][].T, float64[][])\n    - rotfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][].T, float64[][].T)"},{
    "divfft_from_vecfft",
    (PyCFunction)__pythran_wrapall_divfft_from_vecfft,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n\n    - divfft_from_vecfft(complex128[][], complex128[][], float64[][], float64[][])\n    - divfft_from_vecfft(complex128[][], complex128[][], float64[][], float64[][].T)\n    - divfft_from_vecfft(complex128[][], complex128[][], float64[][].T, float64[][])\n    - divfft_from_vecfft(complex128[][], complex128[][], float64[][].T, float64[][].T)\n    - divfft_from_vecfft(complex128[][], complex128[][].T, float64[][], float64[][])\n    - divfft_from_vecfft(complex128[][], complex128[][].T, float64[][], float64[][].T)\n    - divfft_from_vecfft(complex128[][], complex128[][].T, float64[][].T, float64[][])\n    - divfft_from_vecfft(complex128[][], complex128[][].T, float64[][].T, float64[][].T)\n    - divfft_from_vecfft(complex128[][].T, complex128[][], float64[][], float64[][])\n    - divfft_from_vecfft(complex128[][].T, complex128[][], float64[][], float64[][].T)\n    - divfft_from_vecfft(complex128[][].T, complex128[][], float64[][].T, float64[][])\n    - divfft_from_vecfft(complex128[][].T, complex128[][], float64[][].T, float64[][].T)\n    - divfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][], float64[][])\n    - divfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][], float64[][].T)\n    - divfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][].T, float64[][])\n    - divfft_from_vecfft(complex128[][].T, complex128[][].T, float64[][].T, float64[][].T)"},{
    "gradfft_from_fft",
    (PyCFunction)__pythran_wrapall_gradfft_from_fft,
    METH_VARARGS | METH_KEYWORDS,
    "Return the gradient of f_fft in spectral space.\n\n    Supported prototypes:\n\n    - gradfft_from_fft(complex128[][], float64[][], float64[][])\n    - gradfft_from_fft(complex128[][], float64[][], float64[][].T)\n    - gradfft_from_fft(complex128[][], float64[][].T, float64[][])\n    - gradfft_from_fft(complex128[][], float64[][].T, float64[][].T)\n    - gradfft_from_fft(complex128[][].T, float64[][], float64[][])\n    - gradfft_from_fft(complex128[][].T, float64[][], float64[][].T)\n    - gradfft_from_fft(complex128[][].T, float64[][].T, float64[][])\n    - gradfft_from_fft(complex128[][].T, float64[][].T, float64[][].T)"},{
    "vecfft_from_divfft",
    (PyCFunction)__pythran_wrapall_vecfft_from_divfft,
    METH_VARARGS | METH_KEYWORDS,
    "Return the velocity in spectral space computed from the divergence.\n\n\n    Supported prototypes:\n\n    - vecfft_from_divfft(complex128[][], float64[][], float64[][])\n    - vecfft_from_divfft(complex128[][], float64[][], float64[][].T)\n    - vecfft_from_divfft(complex128[][], float64[][].T, float64[][])\n    - vecfft_from_divfft(complex128[][], float64[][].T, float64[][].T)\n    - vecfft_from_divfft(complex128[][].T, float64[][], float64[][])\n    - vecfft_from_divfft(complex128[][].T, float64[][], float64[][].T)\n    - vecfft_from_divfft(complex128[][].T, float64[][].T, float64[][])\n    - vecfft_from_divfft(complex128[][].T, float64[][].T, float64[][].T)"},{
    "vecfft_from_rotfft",
    (PyCFunction)__pythran_wrapall_vecfft_from_rotfft,
    METH_VARARGS | METH_KEYWORDS,
    "Return the velocity in spectral space computed from the rotational.\n\n\n    Supported prototypes:\n\n    - vecfft_from_rotfft(complex128[][], float64[][], float64[][])\n    - vecfft_from_rotfft(complex128[][], float64[][], float64[][].T)\n    - vecfft_from_rotfft(complex128[][], float64[][].T, float64[][])\n    - vecfft_from_rotfft(complex128[][], float64[][].T, float64[][].T)\n    - vecfft_from_rotfft(complex128[][].T, float64[][], float64[][])\n    - vecfft_from_rotfft(complex128[][].T, float64[][], float64[][].T)\n    - vecfft_from_rotfft(complex128[][].T, float64[][].T, float64[][])\n    - vecfft_from_rotfft(complex128[][].T, float64[][].T, float64[][].T)"},{
    "dealiasing_variable",
    (PyCFunction)__pythran_wrapall_dealiasing_variable,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n\n    - dealiasing_variable(complex128[][], uint8[][], int, int)\n    - dealiasing_variable(complex128[][], uint8[][].T, int, int)\n    - dealiasing_variable(complex128[][].T, uint8[][], int, int)\n    - dealiasing_variable(complex128[][].T, uint8[][].T, int, int)"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "util_pythran",            /* m_name */
    "\n\n[pythran]\ncomplex_hook = True\n\n",         /* m_doc */
    -1,                  /* m_size */
    Methods,             /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };
#define PYTHRAN_RETURN return theModule
#define PYTHRAN_MODULE_INIT(s) PyInit_##s
#else
#define PYTHRAN_RETURN return
#define PYTHRAN_MODULE_INIT(s) init##s
#endif
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(util_pythran)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
__attribute__ ((externally_visible))
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(util_pythran)(void) {
    #ifdef PYTHONIC_TYPES_NDARRAY_HPP
        import_array()
    #endif
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("util_pythran",
                                         Methods,
                                         "\n\n[pythran]\ncomplex_hook = True\n\n"
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.8.5",
                                      "2018-06-30 16:25:54.306430",
                                      "35f129d2ce4511cf1e55c8a850281ab786a8fc4fc01eb9d2f1f01532d9ec1ef0");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);


    PYTHRAN_RETURN;
}

#endif