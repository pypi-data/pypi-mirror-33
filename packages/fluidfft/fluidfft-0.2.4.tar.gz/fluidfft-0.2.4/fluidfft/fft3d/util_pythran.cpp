#define BOOST_SIMD_NO_STRICT_ALIASING 1
#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/complex128.hpp>
#include <pythonic/types/complex128.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/include/numpy/empty_like.hpp>
#include <pythonic/include/operator_/div.hpp>
#include <pythonic/include/numpy/sqrt.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/include/__builtin__/len.hpp>
#include <pythonic/include/__builtin__/int_.hpp>
#include <pythonic/include/__builtin__/tuple.hpp>
#include <pythonic/include/operator_/idiv.hpp>
#include <pythonic/include/numpy/zeros.hpp>
#include <pythonic/include/__builtin__/getattr.hpp>
#include <pythonic/include/types/complex.hpp>
#include <pythonic/include/__builtin__/range.hpp>
#include <pythonic/include/__builtin__/None.hpp>
#include <pythonic/numpy/empty_like.hpp>
#include <pythonic/operator_/div.hpp>
#include <pythonic/numpy/sqrt.hpp>
#include <pythonic/types/str.hpp>
#include <pythonic/__builtin__/len.hpp>
#include <pythonic/__builtin__/int_.hpp>
#include <pythonic/__builtin__/tuple.hpp>
#include <pythonic/operator_/idiv.hpp>
#include <pythonic/numpy/zeros.hpp>
#include <pythonic/__builtin__/getattr.hpp>
#include <pythonic/types/complex.hpp>
#include <pythonic/__builtin__/range.hpp>
#include <pythonic/__builtin__/None.hpp>
namespace __pythran_util_pythran
{
  struct loop_spectra3d
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type0;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type0>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type3;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type2>())) __type4;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type4>::type>::type __type5;
      typedef typename pythonic::lazy<__type5>::type __type6;
      typedef decltype(std::declval<__type3>()(std::declval<__type6>())) __type7;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type7>::type::iterator>::value_type>::type __type8;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type4>::type>::type __type9;
      typedef typename pythonic::lazy<__type9>::type __type10;
      typedef decltype(std::declval<__type3>()(std::declval<__type10>())) __type11;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type11>::type::iterator>::value_type>::type __type12;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type4>::type>::type __type13;
      typedef typename pythonic::lazy<__type13>::type __type14;
      typedef decltype(std::declval<__type3>()(std::declval<__type14>())) __type15;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type15>::type::iterator>::value_type>::type __type16;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type8>(), std::declval<__type12>(), std::declval<__type16>())) __type17;
      typedef decltype(std::declval<__type2>()[std::declval<__type17>()]) __type18;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::zeros{})>::type>::type __type19;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::len{})>::type>::type __type20;
      typedef container<typename std::remove_reference<__type1>::type> __type21;
      typedef typename __combined<__type0,__type21>::type __type22;
      typedef typename pythonic::assignable<decltype(std::declval<__type20>()(std::declval<__type22>()))>::type __type23;
      typedef typename pythonic::assignable<decltype(std::declval<__type19>()(std::declval<__type23>()))>::type __type24;
      typedef long __type25;
      typedef decltype((std::declval<__type23>() - std::declval<__type25>())) __type26;
      typedef typename pythonic::lazy<__type26>::type __type27;
      typedef indexable<__type27> __type28;
      typedef typename __combined<__type24,__type28>::type __type29;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::int_{})>::type>::type __type30;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::sqrt{})>::type>::type __type31;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type32;
      typedef decltype(std::declval<__type32>()[std::declval<__type17>()]) __type33;
      typedef typename pythonic::assignable<decltype(std::declval<__type31>()(std::declval<__type33>()))>::type __type34;
      typedef typename pythonic::assignable<typename std::tuple_element<1,typename std::remove_reference<__type0>::type>::type>::type __type35;
      typedef decltype((pythonic::operator_::div(std::declval<__type34>(), std::declval<__type35>()))) __type36;
      typedef typename pythonic::assignable<decltype(std::declval<__type30>()(std::declval<__type36>()))>::type __type37;
      typedef indexable<__type37> __type38;
      typedef typename __combined<__type29,__type38>::type __type39;
      typedef decltype((std::declval<__type37>() + std::declval<__type25>())) __type40;
      typedef indexable<__type40> __type41;
      typedef typename __combined<__type39,__type41>::type __type42;
      typedef typename __combined<__type42,__type28>::type __type43;
      typedef typename pythonic::assignable<decltype(std::declval<__type2>()[std::declval<__type17>()])>::type __type44;
      typedef container<typename std::remove_reference<__type44>::type> __type45;
      typedef typename __combined<__type43,__type45>::type __type46;
      typedef typename __combined<__type46,__type38>::type __type47;
      typedef decltype(std::declval<__type22>()[std::declval<__type37>()]) __type48;
      typedef decltype((std::declval<__type34>() - std::declval<__type48>())) __type49;
      typedef typename pythonic::assignable<decltype((pythonic::operator_::div(std::declval<__type49>(), std::declval<__type35>())))>::type __type50;
      typedef decltype((std::declval<__type25>() - std::declval<__type50>())) __type51;
      typedef decltype((std::declval<__type51>() * std::declval<__type44>())) __type52;
      typedef container<typename std::remove_reference<__type52>::type> __type53;
      typedef typename __combined<__type47,__type53>::type __type54;
      typedef typename __combined<__type54,__type41>::type __type55;
      typedef decltype((std::declval<__type50>() * std::declval<__type44>())) __type56;
      typedef container<typename std::remove_reference<__type56>::type> __type57;
      typedef __type1 __ptype0;
      typedef __type18 __ptype1;
      typedef typename pythonic::returnable<typename __combined<__type55,__type57>::type>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0&& spectrum_k0k1k2, argument_type1&& ks, argument_type2&& K2) const
    ;
  }  ;
  struct vector_product
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
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
      typedef typename std::tuple_element<2,typename std::remove_reference<__type2>::type>::type __type11;
      typedef typename pythonic::lazy<__type11>::type __type12;
      typedef decltype(std::declval<__type1>()(std::declval<__type12>())) __type13;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type13>::type::iterator>::value_type>::type __type14;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type6>(), std::declval<__type10>(), std::declval<__type14>())) __type15;
      typedef decltype(std::declval<__type0>()[std::declval<__type15>()]) __type16;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type17;
      typedef decltype(std::declval<__type17>()[std::declval<__type15>()]) __type18;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type19;
      typedef decltype(std::declval<__type19>()[std::declval<__type15>()]) __type20;
      typedef container<typename std::remove_reference<__type20>::type> __type21;
      typedef typename __combined<__type19,__type21>::type __type22;
      typedef typename pythonic::assignable<decltype(std::declval<__type17>()[std::declval<__type15>()])>::type __type23;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type5>::type>::type __type24;
      typedef typename pythonic::assignable<decltype(std::declval<__type24>()[std::declval<__type15>()])>::type __type25;
      typedef decltype((std::declval<__type23>() * std::declval<__type25>())) __type26;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type27;
      typedef typename pythonic::assignable<decltype(std::declval<__type27>()[std::declval<__type15>()])>::type __type28;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type29;
      typedef typename pythonic::assignable<decltype(std::declval<__type29>()[std::declval<__type15>()])>::type __type30;
      typedef decltype((std::declval<__type28>() * std::declval<__type30>())) __type31;
      typedef decltype((std::declval<__type26>() - std::declval<__type31>())) __type32;
      typedef container<typename std::remove_reference<__type32>::type> __type33;
      typedef typename __combined<__type22,__type33>::type __type34;
      typedef indexable<__type15> __type35;
      typedef typename __combined<__type34,__type35>::type __type36;
      typedef typename __combined<__type36,__type33>::type __type37;
      typedef decltype(std::declval<__type29>()[std::declval<__type15>()]) __type38;
      typedef container<typename std::remove_reference<__type38>::type> __type39;
      typedef typename __combined<__type29,__type39>::type __type40;
      typedef typename pythonic::assignable<decltype(std::declval<__type19>()[std::declval<__type15>()])>::type __type41;
      typedef decltype((std::declval<__type28>() * std::declval<__type41>())) __type42;
      typedef typename pythonic::assignable<decltype(std::declval<__type0>()[std::declval<__type15>()])>::type __type43;
      typedef decltype((std::declval<__type43>() * std::declval<__type25>())) __type44;
      typedef decltype((std::declval<__type42>() - std::declval<__type44>())) __type45;
      typedef container<typename std::remove_reference<__type45>::type> __type46;
      typedef typename __combined<__type40,__type46>::type __type47;
      typedef typename __combined<__type47,__type35>::type __type48;
      typedef typename __combined<__type48,__type46>::type __type49;
      typedef decltype(std::declval<__type24>()[std::declval<__type15>()]) __type50;
      typedef container<typename std::remove_reference<__type50>::type> __type51;
      typedef typename __combined<__type24,__type51>::type __type52;
      typedef decltype((std::declval<__type43>() * std::declval<__type30>())) __type53;
      typedef decltype((std::declval<__type23>() * std::declval<__type41>())) __type54;
      typedef decltype((std::declval<__type53>() - std::declval<__type54>())) __type55;
      typedef container<typename std::remove_reference<__type55>::type> __type56;
      typedef typename __combined<__type52,__type56>::type __type57;
      typedef typename __combined<__type57,__type35>::type __type58;
      typedef typename __combined<__type58,__type56>::type __type59;
      typedef __type16 __ptype2;
      typedef __type18 __ptype3;
      typedef typename pythonic::returnable<decltype(pythonic::types::make_tuple(std::declval<__type37>(), std::declval<__type49>(), std::declval<__type59>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type operator()(argument_type0&& ax, argument_type1&& ay, argument_type2&& az, argument_type3&& bx, argument_type4&& by, argument_type5&& bz) const
    ;
  }  ;
  struct rotfft_from_vecfft_outin
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 , typename argument_type6 , typename argument_type7 , typename argument_type8 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type2>())) __type3;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type3>::type>::type __type4;
      typedef typename pythonic::lazy<__type4>::type __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type5>())) __type6;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type6>::type::iterator>::value_type>::type __type7;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type3>::type>::type __type8;
      typedef typename pythonic::lazy<__type8>::type __type9;
      typedef decltype(std::declval<__type1>()(std::declval<__type9>())) __type10;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type10>::type::iterator>::value_type>::type __type11;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type3>::type>::type __type12;
      typedef typename pythonic::lazy<__type12>::type __type13;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>())) __type14;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type14>::type::iterator>::value_type>::type __type15;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type7>(), std::declval<__type11>(), std::declval<__type15>())) __type16;
      typedef decltype(std::declval<__type0>()[std::declval<__type16>()]) __type17;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type18;
      typedef decltype(std::declval<__type18>()[std::declval<__type16>()]) __type19;
      typedef __type17 __ptype20;
      typedef __type19 __ptype21;
      typedef typename pythonic::returnable<pythonic::types::none_type>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 , typename argument_type6 , typename argument_type7 , typename argument_type8 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5, argument_type6, argument_type7, argument_type8>::result_type operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& Kx, argument_type4&& Ky, argument_type5&& Kz, argument_type6&& rotxfft, argument_type7&& rotyfft, argument_type8&& rotzfft) const
    ;
  }  ;
  struct rotfft_from_vecfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type2>())) __type3;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type3>::type>::type __type4;
      typedef typename pythonic::lazy<__type4>::type __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type5>())) __type6;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type6>::type::iterator>::value_type>::type __type7;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type3>::type>::type __type8;
      typedef typename pythonic::lazy<__type8>::type __type9;
      typedef decltype(std::declval<__type1>()(std::declval<__type9>())) __type10;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type10>::type::iterator>::value_type>::type __type11;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type3>::type>::type __type12;
      typedef typename pythonic::lazy<__type12>::type __type13;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>())) __type14;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type14>::type::iterator>::value_type>::type __type15;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type7>(), std::declval<__type11>(), std::declval<__type15>())) __type16;
      typedef decltype(std::declval<__type0>()[std::declval<__type16>()]) __type17;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type18;
      typedef decltype(std::declval<__type18>()[std::declval<__type16>()]) __type19;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::empty_like{})>::type>::type __type20;
      typedef typename pythonic::assignable<decltype(std::declval<__type20>()(std::declval<__type2>()))>::type __type21;
      typedef indexable<__type16> __type22;
      typedef typename __combined<__type21,__type22>::type __type23;
      typedef std::complex<double> __type24;
      typedef typename pythonic::assignable<decltype(std::declval<__type18>()[std::declval<__type16>()])>::type __type25;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type26;
      typedef typename pythonic::assignable<decltype(std::declval<__type26>()[std::declval<__type16>()])>::type __type27;
      typedef decltype((std::declval<__type25>() * std::declval<__type27>())) __type28;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type5>::type>::type __type29;
      typedef typename pythonic::assignable<decltype(std::declval<__type29>()[std::declval<__type16>()])>::type __type30;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type31;
      typedef typename pythonic::assignable<decltype(std::declval<__type31>()[std::declval<__type16>()])>::type __type32;
      typedef decltype((std::declval<__type30>() * std::declval<__type32>())) __type33;
      typedef decltype((std::declval<__type28>() - std::declval<__type33>())) __type34;
      typedef decltype((std::declval<__type24>() * std::declval<__type34>())) __type35;
      typedef container<typename std::remove_reference<__type35>::type> __type36;
      typedef typename __combined<__type23,__type36>::type __type37;
      typedef typename __combined<__type37,__type22>::type __type38;
      typedef typename __combined<__type38,__type36>::type __type39;
      typedef typename pythonic::assignable<decltype(std::declval<__type2>()[std::declval<__type16>()])>::type __type40;
      typedef decltype((std::declval<__type30>() * std::declval<__type40>())) __type41;
      typedef typename pythonic::assignable<decltype(std::declval<__type0>()[std::declval<__type16>()])>::type __type42;
      typedef decltype((std::declval<__type42>() * std::declval<__type27>())) __type43;
      typedef decltype((std::declval<__type41>() - std::declval<__type43>())) __type44;
      typedef decltype((std::declval<__type24>() * std::declval<__type44>())) __type45;
      typedef container<typename std::remove_reference<__type45>::type> __type46;
      typedef typename __combined<__type23,__type46>::type __type47;
      typedef typename __combined<__type47,__type22>::type __type48;
      typedef typename __combined<__type48,__type46>::type __type49;
      typedef decltype((std::declval<__type42>() * std::declval<__type32>())) __type50;
      typedef decltype((std::declval<__type25>() * std::declval<__type40>())) __type51;
      typedef decltype((std::declval<__type50>() - std::declval<__type51>())) __type52;
      typedef decltype((std::declval<__type24>() * std::declval<__type52>())) __type53;
      typedef container<typename std::remove_reference<__type53>::type> __type54;
      typedef typename __combined<__type23,__type54>::type __type55;
      typedef typename __combined<__type55,__type22>::type __type56;
      typedef typename __combined<__type56,__type54>::type __type57;
      typedef __type17 __ptype38;
      typedef __type19 __ptype39;
      typedef typename pythonic::returnable<decltype(pythonic::types::make_tuple(std::declval<__type39>(), std::declval<__type49>(), std::declval<__type57>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& Kx, argument_type4&& Ky, argument_type5&& Kz) const
    ;
  }  ;
  struct divfft_from_vecfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
    struct type
    {
      typedef std::complex<double> __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype((std::declval<__type1>() * std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type5;
      typedef decltype((std::declval<__type4>() * std::declval<__type5>())) __type6;
      typedef decltype((std::declval<__type3>() + std::declval<__type6>())) __type7;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type5>::type>::type __type8;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type9;
      typedef decltype((std::declval<__type8>() * std::declval<__type9>())) __type10;
      typedef decltype((std::declval<__type7>() + std::declval<__type10>())) __type11;
      typedef typename pythonic::returnable<decltype((std::declval<__type0>() * std::declval<__type11>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& kx, argument_type4&& ky, argument_type5&& kz) const
    ;
  }  ;
  struct project_perpk3d
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 , typename argument_type6 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type2>())) __type3;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type3>::type>::type __type4;
      typedef typename pythonic::lazy<__type4>::type __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type5>())) __type6;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type6>::type::iterator>::value_type>::type __type7;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type3>::type>::type __type8;
      typedef typename pythonic::lazy<__type8>::type __type9;
      typedef decltype(std::declval<__type1>()(std::declval<__type9>())) __type10;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type10>::type::iterator>::value_type>::type __type11;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type3>::type>::type __type12;
      typedef typename pythonic::lazy<__type12>::type __type13;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>())) __type14;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type14>::type::iterator>::value_type>::type __type15;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type7>(), std::declval<__type11>(), std::declval<__type15>())) __type16;
      typedef decltype(std::declval<__type0>()[std::declval<__type16>()]) __type17;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type18;
      typedef decltype(std::declval<__type18>()[std::declval<__type16>()]) __type19;
      typedef __type17 __ptype44;
      typedef __type19 __ptype45;
      typedef typename pythonic::returnable<pythonic::types::none_type>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 , typename argument_type6 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5, argument_type6>::result_type operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& Kx, argument_type4&& Ky, argument_type5&& Kz, argument_type6&& inv_K_square_nozero) const
    ;
  }  ;
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
  typename loop_spectra3d::type<argument_type0, argument_type1, argument_type2>::result_type loop_spectra3d::operator()(argument_type0&& spectrum_k0k1k2, argument_type1&& ks, argument_type2&& K2) const
  {
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::zeros{})>::type>::type __type0;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::len{})>::type>::type __type1;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type2;
    typedef typename std::tuple_element<1,typename std::remove_reference<__type2>::type>::type __type3;
    typedef container<typename std::remove_reference<__type3>::type> __type4;
    typedef typename __combined<__type2,__type4>::type __type5;
    typedef typename pythonic::assignable<decltype(std::declval<__type1>()(std::declval<__type5>()))>::type __type6;
    typedef typename pythonic::assignable<decltype(std::declval<__type0>()(std::declval<__type6>()))>::type __type7;
    typedef long __type8;
    typedef decltype((std::declval<__type6>() - std::declval<__type8>())) __type9;
    typedef typename pythonic::lazy<__type9>::type __type10;
    typedef indexable<__type10> __type11;
    typedef typename __combined<__type7,__type11>::type __type12;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::int_{})>::type>::type __type13;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::sqrt{})>::type>::type __type14;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type15;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type16;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type17;
    typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type17>())) __type18;
    typedef typename std::tuple_element<0,typename std::remove_reference<__type18>::type>::type __type19;
    typedef typename pythonic::lazy<__type19>::type __type20;
    typedef decltype(std::declval<__type16>()(std::declval<__type20>())) __type21;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type21>::type::iterator>::value_type>::type __type22;
    typedef typename std::tuple_element<1,typename std::remove_reference<__type18>::type>::type __type23;
    typedef typename pythonic::lazy<__type23>::type __type24;
    typedef decltype(std::declval<__type16>()(std::declval<__type24>())) __type25;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type25>::type::iterator>::value_type>::type __type26;
    typedef typename std::tuple_element<2,typename std::remove_reference<__type18>::type>::type __type27;
    typedef typename pythonic::lazy<__type27>::type __type28;
    typedef decltype(std::declval<__type16>()(std::declval<__type28>())) __type29;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type29>::type::iterator>::value_type>::type __type30;
    typedef decltype(pythonic::types::make_tuple(std::declval<__type22>(), std::declval<__type26>(), std::declval<__type30>())) __type31;
    typedef decltype(std::declval<__type15>()[std::declval<__type31>()]) __type32;
    typedef typename pythonic::assignable<decltype(std::declval<__type14>()(std::declval<__type32>()))>::type __type33;
    typedef typename pythonic::assignable<typename std::tuple_element<1,typename std::remove_reference<__type2>::type>::type>::type __type34;
    typedef decltype((pythonic::operator_::div(std::declval<__type33>(), std::declval<__type34>()))) __type35;
    typedef typename pythonic::assignable<decltype(std::declval<__type13>()(std::declval<__type35>()))>::type __type36;
    typedef indexable<__type36> __type37;
    typedef typename __combined<__type12,__type37>::type __type38;
    typedef decltype((std::declval<__type36>() + std::declval<__type8>())) __type39;
    typedef indexable<__type39> __type40;
    typedef typename __combined<__type38,__type40>::type __type41;
    typedef typename __combined<__type41,__type11>::type __type42;
    typedef typename pythonic::assignable<decltype(std::declval<__type17>()[std::declval<__type31>()])>::type __type43;
    typedef container<typename std::remove_reference<__type43>::type> __type44;
    typedef typename __combined<__type42,__type44>::type __type45;
    typedef typename __combined<__type45,__type37>::type __type46;
    typedef decltype(std::declval<__type5>()[std::declval<__type36>()]) __type47;
    typedef decltype((std::declval<__type33>() - std::declval<__type47>())) __type48;
    typedef typename pythonic::assignable<decltype((pythonic::operator_::div(std::declval<__type48>(), std::declval<__type34>())))>::type __type49;
    typedef decltype((std::declval<__type8>() - std::declval<__type49>())) __type50;
    typedef decltype((std::declval<__type50>() * std::declval<__type43>())) __type51;
    typedef container<typename std::remove_reference<__type51>::type> __type52;
    typedef typename __combined<__type46,__type52>::type __type53;
    typedef typename __combined<__type53,__type40>::type __type54;
    typedef decltype((std::declval<__type49>() * std::declval<__type43>())) __type55;
    typedef container<typename std::remove_reference<__type55>::type> __type56;
    typename pythonic::assignable<decltype(std::get<1>(ks))>::type deltak = std::get<1>(ks);
    typename pythonic::assignable<decltype(pythonic::__builtin__::functor::len{}(ks))>::type nk = pythonic::__builtin__::functor::len{}(ks);
    typename pythonic::assignable<typename __combined<__type54,__type56>::type>::type spectrum3d = pythonic::numpy::functor::zeros{}(nk);
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(spectrum_k0k1k2)))>::type nk0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(spectrum_k0k1k2));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(spectrum_k0k1k2)))>::type nk1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(spectrum_k0k1k2));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(spectrum_k0k1k2)))>::type nk2 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(spectrum_k0k1k2));
    {
      long  __target1 = nk0;
      for (long  ik0=0L; ik0 < __target1; ik0 += 1L)
      {
        {
          long  __target2 = nk1;
          for (long  ik1=0L; ik1 < __target2; ik1 += 1L)
          {
            {
              long  __target3 = nk2;
              for (long  ik2=0L; ik2 < __target3; ik2 += 1L)
              {
                typename pythonic::assignable<decltype(spectrum_k0k1k2.fast(pythonic::types::make_tuple(ik0, ik1, ik2)))>::type value = spectrum_k0k1k2.fast(pythonic::types::make_tuple(ik0, ik1, ik2));
                typename pythonic::assignable<decltype(pythonic::numpy::functor::sqrt{}(K2.fast(pythonic::types::make_tuple(ik0, ik1, ik2))))>::type kappa = pythonic::numpy::functor::sqrt{}(K2.fast(pythonic::types::make_tuple(ik0, ik1, ik2)));
                typename pythonic::assignable<decltype(pythonic::__builtin__::functor::int_{}((pythonic::operator_::div(kappa, deltak))))>::type ik = pythonic::__builtin__::functor::int_{}((pythonic::operator_::div(kappa, deltak)));
                {
                  typename pythonic::assignable<typename pythonic::assignable<decltype((pythonic::operator_::div(std::declval<__type48>(), std::declval<__type34>())))>::type>::type coef_share;
                  if ((ik >= (nk - 1L)))
                  {
                    typename pythonic::lazy<decltype((nk - 1L))>::type ik_ = (nk - 1L);
                    spectrum3d[ik_] += value;
                  }
                  else
                  {
                    coef_share = (pythonic::operator_::div((kappa - ks[ik]), deltak));
                    spectrum3d[ik] += ((1L - coef_share) * value);
                    spectrum3d[(ik + 1L)] += (coef_share * value);
                  }
                }
              }
            }
          }
        }
      }
    }
    return spectrum3d;
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
  typename vector_product::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type vector_product::operator()(argument_type0&& ax, argument_type1&& ay, argument_type2&& az, argument_type3&& bx, argument_type4&& by, argument_type5&& bz) const
  {
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ax)))>::type n0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ax));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ax)))>::type n1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ax));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ax)))>::type n2 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ax));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            {
              long  __target3 = n2;
              for (long  i2=0L; i2 < __target3; i2 += 1L)
              {
                typename pythonic::assignable<decltype(ax.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type elem_ax = ax.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(ay.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type elem_ay = ay.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(az.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type elem_az = az.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(bx.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type elem_bx = bx.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(by.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type elem_by = by.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(bz.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type elem_bz = bz.fast(pythonic::types::make_tuple(i0, i1, i2));
                bx.fast(pythonic::types::make_tuple(i0, i1, i2)) = ((elem_ay * elem_bz) - (elem_az * elem_by));
                by.fast(pythonic::types::make_tuple(i0, i1, i2)) = ((elem_az * elem_bx) - (elem_ax * elem_bz));
                bz.fast(pythonic::types::make_tuple(i0, i1, i2)) = ((elem_ax * elem_by) - (elem_ay * elem_bx));
              }
            }
          }
        }
      }
    }
    return pythonic::types::make_tuple(bx, by, bz);
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 , typename argument_type6 , typename argument_type7 , typename argument_type8 >
  typename rotfft_from_vecfft_outin::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5, argument_type6, argument_type7, argument_type8>::result_type rotfft_from_vecfft_outin::operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& Kx, argument_type4&& Ky, argument_type5&& Kz, argument_type6&& rotxfft, argument_type7&& rotyfft, argument_type8&& rotzfft) const
  {
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n2 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            {
              long  __target3 = n2;
              for (long  i2=0L; i2 < __target3; i2 += 1L)
              {
                typename pythonic::assignable<decltype(Kx.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type kx = Kx.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(Ky.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type ky = Ky.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(Kz.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type kz = Kz.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type vx = vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type vy = vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type vz = vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2));
                rotxfft.fast(pythonic::types::make_tuple(i0, i1, i2)) = (std::complex<double>(0.0, 1.0) * ((ky * vz) - (kz * vy)));
                rotyfft.fast(pythonic::types::make_tuple(i0, i1, i2)) = (std::complex<double>(0.0, 1.0) * ((kz * vx) - (kx * vz)));
                rotzfft.fast(pythonic::types::make_tuple(i0, i1, i2)) = (std::complex<double>(0.0, 1.0) * ((kx * vy) - (ky * vx)));
              }
            }
          }
        }
      }
    }
    return pythonic::__builtin__::None;
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
  typename rotfft_from_vecfft::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type rotfft_from_vecfft::operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& Kx, argument_type4&& Ky, argument_type5&& Kz) const
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
    typedef typename std::tuple_element<2,typename std::remove_reference<__type4>::type>::type __type13;
    typedef typename pythonic::lazy<__type13>::type __type14;
    typedef decltype(std::declval<__type3>()(std::declval<__type14>())) __type15;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type15>::type::iterator>::value_type>::type __type16;
    typedef decltype(pythonic::types::make_tuple(std::declval<__type8>(), std::declval<__type12>(), std::declval<__type16>())) __type17;
    typedef indexable<__type17> __type18;
    typedef typename __combined<__type2,__type18>::type __type19;
    typedef std::complex<double> __type20;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type21;
    typedef typename pythonic::assignable<decltype(std::declval<__type21>()[std::declval<__type17>()])>::type __type22;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type23;
    typedef typename pythonic::assignable<decltype(std::declval<__type23>()[std::declval<__type17>()])>::type __type24;
    typedef decltype((std::declval<__type22>() * std::declval<__type24>())) __type25;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type5>::type>::type __type26;
    typedef typename pythonic::assignable<decltype(std::declval<__type26>()[std::declval<__type17>()])>::type __type27;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type28;
    typedef typename pythonic::assignable<decltype(std::declval<__type28>()[std::declval<__type17>()])>::type __type29;
    typedef decltype((std::declval<__type27>() * std::declval<__type29>())) __type30;
    typedef decltype((std::declval<__type25>() - std::declval<__type30>())) __type31;
    typedef decltype((std::declval<__type20>() * std::declval<__type31>())) __type32;
    typedef container<typename std::remove_reference<__type32>::type> __type33;
    typedef typename __combined<__type19,__type33>::type __type34;
    typedef typename pythonic::assignable<decltype(std::declval<__type1>()[std::declval<__type17>()])>::type __type35;
    typedef decltype((std::declval<__type27>() * std::declval<__type35>())) __type36;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type37;
    typedef typename pythonic::assignable<decltype(std::declval<__type37>()[std::declval<__type17>()])>::type __type38;
    typedef decltype((std::declval<__type38>() * std::declval<__type24>())) __type39;
    typedef decltype((std::declval<__type36>() - std::declval<__type39>())) __type40;
    typedef decltype((std::declval<__type20>() * std::declval<__type40>())) __type41;
    typedef container<typename std::remove_reference<__type41>::type> __type42;
    typedef typename __combined<__type19,__type42>::type __type43;
    typedef decltype((std::declval<__type38>() * std::declval<__type29>())) __type44;
    typedef decltype((std::declval<__type22>() * std::declval<__type35>())) __type45;
    typedef decltype((std::declval<__type44>() - std::declval<__type45>())) __type46;
    typedef decltype((std::declval<__type20>() * std::declval<__type46>())) __type47;
    typedef container<typename std::remove_reference<__type47>::type> __type48;
    typedef typename __combined<__type19,__type48>::type __type49;
    typename pythonic::assignable<typename __combined<__type34,__type18>::type>::type rotxfft = pythonic::numpy::functor::empty_like{}(vx_fft);
    typename pythonic::assignable<typename __combined<__type43,__type18>::type>::type rotyfft = pythonic::numpy::functor::empty_like{}(vx_fft);
    typename pythonic::assignable<typename __combined<__type49,__type18>::type>::type rotzfft = pythonic::numpy::functor::empty_like{}(vx_fft);
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n2 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            {
              long  __target3 = n2;
              for (long  i2=0L; i2 < __target3; i2 += 1L)
              {
                typename pythonic::assignable<decltype(Kx.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type kx = Kx.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(Ky.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type ky = Ky.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(Kz.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type kz = Kz.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type vx = vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type vy = vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type vz = vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2));
                rotxfft.fast(pythonic::types::make_tuple(i0, i1, i2)) = (std::complex<double>(0.0, 1.0) * ((ky * vz) - (kz * vy)));
                rotyfft.fast(pythonic::types::make_tuple(i0, i1, i2)) = (std::complex<double>(0.0, 1.0) * ((kz * vx) - (kx * vz)));
                rotzfft.fast(pythonic::types::make_tuple(i0, i1, i2)) = (std::complex<double>(0.0, 1.0) * ((kx * vy) - (ky * vx)));
              }
            }
          }
        }
      }
    }
    return pythonic::types::make_tuple(rotxfft, rotyfft, rotzfft);
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
  typename divfft_from_vecfft::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type divfft_from_vecfft::operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& kx, argument_type4&& ky, argument_type5&& kz) const
  {
    return (std::complex<double>(0.0, 1.0) * (((kx * vx_fft) + (ky * vy_fft)) + (kz * vz_fft)));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 , typename argument_type6 >
  typename project_perpk3d::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5, argument_type6>::result_type project_perpk3d::operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& vz_fft, argument_type3&& Kx, argument_type4&& Ky, argument_type5&& Kz, argument_type6&& inv_K_square_nozero) const
  {
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft)))>::type n2 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(vx_fft));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            {
              long  __target3 = n2;
              for (long  i2=0L; i2 < __target3; i2 += 1L)
              {
                typename pythonic::assignable<decltype(Kx.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type kx = Kx.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(Ky.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type ky = Ky.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(Kz.fast(pythonic::types::make_tuple(i0, i1, i2)))>::type kz = Kz.fast(pythonic::types::make_tuple(i0, i1, i2));
                typename pythonic::assignable<decltype(((((kx * vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2))) + (ky * vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))) + (kz * vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))) * inv_K_square_nozero.fast(pythonic::types::make_tuple(i0, i1, i2))))>::type tmp = ((((kx * vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2))) + (ky * vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))) + (kz * vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2)))) * inv_K_square_nozero.fast(pythonic::types::make_tuple(i0, i1, i2)));
                vx_fft.fast(pythonic::types::make_tuple(i0, i1, i2)) -= (kx * tmp);
                vy_fft.fast(pythonic::types::make_tuple(i0, i1, i2)) -= (ky * tmp);
                vz_fft.fast(pythonic::types::make_tuple(i0, i1, i2)) -= (kz * tmp);
              }
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
typename __pythran_util_pythran::loop_spectra3d::type<pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,1>, pythonic::types::ndarray<double,3>>::result_type loop_spectra3d0(pythonic::types::ndarray<double,3>&& spectrum_k0k1k2, pythonic::types::ndarray<double,1>&& ks, pythonic::types::ndarray<double,3>&& K2) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::loop_spectra3d()(spectrum_k0k1k2, ks, K2);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::vector_product::type<pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>>::result_type vector_product0(pythonic::types::ndarray<double,3>&& ax, pythonic::types::ndarray<double,3>&& ay, pythonic::types::ndarray<double,3>&& az, pythonic::types::ndarray<double,3>&& bx, pythonic::types::ndarray<double,3>&& by, pythonic::types::ndarray<double,3>&& bz) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::vector_product()(ax, ay, az, bx, by, bz);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft_outin::type<pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>>::result_type rotfft_from_vecfft_outin0(pythonic::types::ndarray<std::complex<double>,3>&& vx_fft, pythonic::types::ndarray<std::complex<double>,3>&& vy_fft, pythonic::types::ndarray<std::complex<double>,3>&& vz_fft, pythonic::types::ndarray<double,3>&& Kx, pythonic::types::ndarray<double,3>&& Ky, pythonic::types::ndarray<double,3>&& Kz, pythonic::types::ndarray<std::complex<double>,3>&& rotxfft, pythonic::types::ndarray<std::complex<double>,3>&& rotyfft, pythonic::types::ndarray<std::complex<double>,3>&& rotzfft) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft_outin()(vx_fft, vy_fft, vz_fft, Kx, Ky, Kz, rotxfft, rotyfft, rotzfft);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::rotfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>>::result_type rotfft_from_vecfft0(pythonic::types::ndarray<std::complex<double>,3>&& vx_fft, pythonic::types::ndarray<std::complex<double>,3>&& vy_fft, pythonic::types::ndarray<std::complex<double>,3>&& vz_fft, pythonic::types::ndarray<double,3>&& Kx, pythonic::types::ndarray<double,3>&& Ky, pythonic::types::ndarray<double,3>&& Kz) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::rotfft_from_vecfft()(vx_fft, vy_fft, vz_fft, Kx, Ky, Kz);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::divfft_from_vecfft::type<pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>>::result_type divfft_from_vecfft0(pythonic::types::ndarray<std::complex<double>,3>&& vx_fft, pythonic::types::ndarray<std::complex<double>,3>&& vy_fft, pythonic::types::ndarray<std::complex<double>,3>&& vz_fft, pythonic::types::ndarray<double,3>&& kx, pythonic::types::ndarray<double,3>&& ky, pythonic::types::ndarray<double,3>&& kz) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::divfft_from_vecfft()(vx_fft, vy_fft, vz_fft, kx, ky, kz);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::project_perpk3d::type<pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>>::result_type project_perpk3d0(pythonic::types::ndarray<std::complex<double>,3>&& vx_fft, pythonic::types::ndarray<std::complex<double>,3>&& vy_fft, pythonic::types::ndarray<std::complex<double>,3>&& vz_fft, pythonic::types::ndarray<double,3>&& Kx, pythonic::types::ndarray<double,3>&& Ky, pythonic::types::ndarray<double,3>&& Kz, pythonic::types::ndarray<double,3>&& inv_K_square_nozero) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::project_perpk3d()(vx_fft, vy_fft, vz_fft, Kx, Ky, Kz, inv_K_square_nozero);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util_pythran::project_perpk3d::type<pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>>::result_type project_perpk3d1(pythonic::types::ndarray<double,3>&& vx_fft, pythonic::types::ndarray<double,3>&& vy_fft, pythonic::types::ndarray<double,3>&& vz_fft, pythonic::types::ndarray<double,3>&& Kx, pythonic::types::ndarray<double,3>&& Ky, pythonic::types::ndarray<double,3>&& Kz, pythonic::types::ndarray<double,3>&& inv_K_square_nozero) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util_pythran::project_perpk3d()(vx_fft, vy_fft, vz_fft, Kx, Ky, Kz, inv_K_square_nozero);
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
__pythran_wrap_loop_spectra3d0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    char const* keywords[] = {"spectrum_k0k1k2","ks","K2", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,1>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[2]))
        return to_python(loop_spectra3d0(from_python<pythonic::types::ndarray<double,3>>(args_obj[0]), from_python<pythonic::types::ndarray<double,1>>(args_obj[1]), from_python<pythonic::types::ndarray<double,3>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_vector_product0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[6+1];
    char const* keywords[] = {"ax","ay","az","bx","by","bz", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[5]))
        return to_python(vector_product0(from_python<pythonic::types::ndarray<double,3>>(args_obj[0]), from_python<pythonic::types::ndarray<double,3>>(args_obj[1]), from_python<pythonic::types::ndarray<double,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<pythonic::types::ndarray<double,3>>(args_obj[4]), from_python<pythonic::types::ndarray<double,3>>(args_obj[5])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft_outin0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[9+1];
    char const* keywords[] = {"vx_fft","vy_fft","vz_fft","Kx","Ky","Kz","rotxfft","rotyfft","rotzfft", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5], &args_obj[6], &args_obj[7], &args_obj[8]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[5]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[6]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[7]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[8]))
        return to_python(rotfft_from_vecfft_outin0(from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<pythonic::types::ndarray<double,3>>(args_obj[4]), from_python<pythonic::types::ndarray<double,3>>(args_obj[5]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[6]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[7]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[8])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_rotfft_from_vecfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[6+1];
    char const* keywords[] = {"vx_fft","vy_fft","vz_fft","Kx","Ky","Kz", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[5]))
        return to_python(rotfft_from_vecfft0(from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<pythonic::types::ndarray<double,3>>(args_obj[4]), from_python<pythonic::types::ndarray<double,3>>(args_obj[5])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_divfft_from_vecfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[6+1];
    char const* keywords[] = {"vx_fft","vy_fft","vz_fft","kx","ky","kz", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[5]))
        return to_python(divfft_from_vecfft0(from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<pythonic::types::ndarray<double,3>>(args_obj[4]), from_python<pythonic::types::ndarray<double,3>>(args_obj[5])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_project_perpk3d0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[7+1];
    char const* keywords[] = {"vx_fft","vy_fft","vz_fft","Kx","Ky","Kz","inv_K_square_nozero", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5], &args_obj[6]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[5]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[6]))
        return to_python(project_perpk3d0(from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<pythonic::types::ndarray<double,3>>(args_obj[4]), from_python<pythonic::types::ndarray<double,3>>(args_obj[5]), from_python<pythonic::types::ndarray<double,3>>(args_obj[6])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_project_perpk3d1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[7+1];
    char const* keywords[] = {"vx_fft","vy_fft","vz_fft","Kx","Ky","Kz","inv_K_square_nozero", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5], &args_obj[6]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[5]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[6]))
        return to_python(project_perpk3d1(from_python<pythonic::types::ndarray<double,3>>(args_obj[0]), from_python<pythonic::types::ndarray<double,3>>(args_obj[1]), from_python<pythonic::types::ndarray<double,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<pythonic::types::ndarray<double,3>>(args_obj[4]), from_python<pythonic::types::ndarray<double,3>>(args_obj[5]), from_python<pythonic::types::ndarray<double,3>>(args_obj[6])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_loop_spectra3d(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_loop_spectra3d0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "loop_spectra3d", "   loop_spectra3d(float64[][][],float64[],float64[][][])", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_vector_product(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_vector_product0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "vector_product", "   vector_product(float64[][][],float64[][][],float64[][][],float64[][][],float64[][][],float64[][][])", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_rotfft_from_vecfft_outin(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_rotfft_from_vecfft_outin0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "rotfft_from_vecfft_outin", "   rotfft_from_vecfft_outin(complex128[][][],complex128[][][],complex128[][][],float64[][][],float64[][][],float64[][][],complex128[][][],complex128[][][],complex128[][][])", args, kw);
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

                return pythonic::python::raise_invalid_argument(
                               "rotfft_from_vecfft", "   rotfft_from_vecfft(complex128[][][],complex128[][][],complex128[][][],float64[][][],float64[][][],float64[][][])", args, kw);
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

                return pythonic::python::raise_invalid_argument(
                               "divfft_from_vecfft", "   divfft_from_vecfft(complex128[][][],complex128[][][],complex128[][][],float64[][][],float64[][][],float64[][][])", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_project_perpk3d(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_project_perpk3d0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_project_perpk3d1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "project_perpk3d", "   project_perpk3d(complex128[][][],complex128[][][],complex128[][][],float64[][][],float64[][][],float64[][][],float64[][][])\n   project_perpk3d(float64[][][],float64[][][],float64[][][],float64[][][],float64[][][],float64[][][],float64[][][])", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "loop_spectra3d",
    (PyCFunction)__pythran_wrapall_loop_spectra3d,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the 3d spectrum.\n\n    Supported prototypes:\n\n    - loop_spectra3d(float64[][][], float64[], float64[][][])"},{
    "vector_product",
    (PyCFunction)__pythran_wrapall_vector_product,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the vector product.\n\n    Supported prototypes:\n\n    - vector_product(float64[][][], float64[][][], float64[][][], float64[][][], float64[][][], float64[][][])\n\n    Warning: the arrays bx, by, bz are overwritten.\n\n"},{
    "rotfft_from_vecfft_outin",
    (PyCFunction)__pythran_wrapall_rotfft_from_vecfft_outin,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the curl of a vector (in spectral space)\n\n    Supported prototypes:\n\n    - rotfft_from_vecfft_outin(complex128[][][], complex128[][][], complex128[][][], float64[][][], float64[][][], float64[][][], complex128[][][], complex128[][][], complex128[][][])"},{
    "rotfft_from_vecfft",
    (PyCFunction)__pythran_wrapall_rotfft_from_vecfft,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the curl of a vector (in spectral space)\n\n    Supported prototypes:\n\n    - rotfft_from_vecfft(complex128[][][], complex128[][][], complex128[][][], float64[][][], float64[][][], float64[][][])"},{
    "divfft_from_vecfft",
    (PyCFunction)__pythran_wrapall_divfft_from_vecfft,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the divergence of a vector (in spectral space)\n\n    Supported prototypes:\n\n    - divfft_from_vecfft(complex128[][][], complex128[][][], complex128[][][], float64[][][], float64[][][], float64[][][])"},{
    "project_perpk3d",
    (PyCFunction)__pythran_wrapall_project_perpk3d,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n\n    - project_perpk3d(complex128[][][], complex128[][][], complex128[][][], float64[][][], float64[][][], float64[][][], float64[][][])\n    - project_perpk3d(float64[][][], float64[][][], float64[][][], float64[][][], float64[][][], float64[][][], float64[][][])"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "util_pythran",            /* m_name */
    "",         /* m_doc */
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
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.8.5",
                                      "2018-06-30 16:25:59.311678",
                                      "0b3c6407ac73b5e219390ebc3e72f7795ca7364d8a5caf35149b9728c4837bcc");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);


    PYTHRAN_RETURN;
}

#endif