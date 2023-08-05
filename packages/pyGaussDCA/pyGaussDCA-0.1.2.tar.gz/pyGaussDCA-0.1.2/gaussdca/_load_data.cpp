#define BOOST_SIMD_NO_STRICT_ALIASING 1
#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/types/str.hpp>
#include <pythonic/types/float.hpp>
#include <pythonic/include/__builtin__/set.hpp>
#include <pythonic/include/__builtin__/list.hpp>
#include <pythonic/include/__builtin__/str/strip.hpp>
#include <pythonic/include/__builtin__/RuntimeError.hpp>
#include <pythonic/include/__builtin__/dict/get.hpp>
#include <pythonic/include/__dispatch__/count.hpp>
#include <pythonic/include/__builtin__/str/startswith.hpp>
#include <pythonic/include/numpy/int8.hpp>
#include <pythonic/include/functools/partial.hpp>
#include <pythonic/include/__builtin__/getattr.hpp>
#include <pythonic/include/operator_/idiv.hpp>
#include <pythonic/include/operator_/div.hpp>
#include <pythonic/include/io/_io/TextIOWrapper/seek.hpp>
#include <pythonic/include/__builtin__/dict.hpp>
#include <pythonic/include/__builtin__/filter.hpp>
#include <pythonic/include/numpy/array.hpp>
#include <pythonic/include/__builtin__/len.hpp>
#include <pythonic/include/__builtin__/map.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/include/__builtin__/in.hpp>
#include <pythonic/include/__builtin__/open.hpp>
#include <pythonic/include/__builtin__/list/append.hpp>
#include <pythonic/__builtin__/set.hpp>
#include <pythonic/__builtin__/list.hpp>
#include <pythonic/__builtin__/str/strip.hpp>
#include <pythonic/__builtin__/RuntimeError.hpp>
#include <pythonic/__builtin__/dict/get.hpp>
#include <pythonic/__dispatch__/count.hpp>
#include <pythonic/__builtin__/str/startswith.hpp>
#include <pythonic/numpy/int8.hpp>
#include <pythonic/functools/partial.hpp>
#include <pythonic/__builtin__/getattr.hpp>
#include <pythonic/operator_/idiv.hpp>
#include <pythonic/operator_/div.hpp>
#include <pythonic/io/_io/TextIOWrapper/seek.hpp>
#include <pythonic/__builtin__/dict.hpp>
#include <pythonic/__builtin__/filter.hpp>
#include <pythonic/numpy/array.hpp>
#include <pythonic/__builtin__/len.hpp>
#include <pythonic/__builtin__/map.hpp>
#include <pythonic/types/str.hpp>
#include <pythonic/__builtin__/in.hpp>
#include <pythonic/__builtin__/open.hpp>
#include <pythonic/__builtin__/list/append.hpp>
namespace __pythran__load_data
{
  struct load_a3m_lambda1
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type1;
      typedef typename pythonic::returnable<decltype((! pythonic::in(std::declval<__type1>(), std::declval<__type0>())))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& lowercase, argument_type1&& ch) const
    ;
  }  ;
  struct load_a3m_lambda0
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::dict::functor::get{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef long __type3;
      typedef __type0 __ptype0;
      typedef __type0 __ptype1;
      typedef typename pythonic::returnable<decltype(std::declval<__type1>()(std::declval<__type2>(), std::declval<__type0>(), std::declval<__type3>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& mapping, argument_type1&& ch) const
    ;
  }  ;
  struct load_a3m
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 = double>
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::array{})>::type>::type __type0;
      typedef typename pythonic::assignable<pythonic::types::empty_list>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::map{})>::type>::type __type2;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::functools::functor::partial{})>::type>::type __type3;
      typedef load_a3m_lambda0 __type4;
      typedef pythonic::types::str __type5;
      typedef long __type6;
      typedef typename pythonic::assignable<pythonic::types::dict<__type5,__type6>>::type __type7;
      typedef decltype(std::declval<__type3>()(std::declval<__type4>(), std::declval<__type7>())) __type8;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::filter{})>::type>::type __type9;
      typedef load_a3m_lambda1 __type10;
      typedef typename pythonic::assignable<pythonic::types::set<__type5>>::type __type11;
      typedef decltype(std::declval<__type3>()(std::declval<__type10>(), std::declval<__type11>())) __type12;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::str::functor::strip{})>::type>::type __type13;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::open{})>::type>::type __type14;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type15;
      typedef typename pythonic::assignable<decltype(std::declval<__type14>()(std::declval<__type15>()))>::type __type16;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type16>::type::iterator>::value_type>::type __type17;
      typedef typename pythonic::assignable<decltype(std::declval<__type13>()(std::declval<__type17>()))>::type __type18;
      typedef decltype(std::declval<__type9>()(std::declval<__type12>(), std::declval<__type18>())) __type19;
      typedef decltype(std::declval<__type2>()(std::declval<__type8>(), std::declval<__type19>())) __type20;
      typedef pythonic::types::list<typename std::remove_reference<__type20>::type> __type21;
      typedef typename __combined<__type1,__type21>::type __type22;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::int8{})>::type>::type __type23;
      typedef decltype(std::declval<__type0>()(std::declval<__type22>(), std::declval<__type23>())) __type24;
      typedef typename pythonic::returnable<decltype(pythonic::__builtin__::getattr<pythonic::types::attr::T>(std::declval<__type24>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 = double>
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& fasta, argument_type1 max_gap_fraction= 0.9) const
    ;
  }  ;
  template <typename argument_type0 , typename argument_type1 >
  typename load_a3m_lambda1::type<argument_type0, argument_type1>::result_type load_a3m_lambda1::operator()(argument_type0&& lowercase, argument_type1&& ch) const
  {
    return (! pythonic::in(lowercase, ch));
  }
  template <typename argument_type0 , typename argument_type1 >
  typename load_a3m_lambda0::type<argument_type0, argument_type1>::result_type load_a3m_lambda0::operator()(argument_type0&& mapping, argument_type1&& ch) const
  {
    return pythonic::__builtin__::dict::functor::get{}(mapping, ch, 22L);
  }
  template <typename argument_type0 , typename argument_type1 >
  typename load_a3m::type<argument_type0, argument_type1>::result_type load_a3m::operator()(argument_type0&& fasta, argument_type1 max_gap_fraction) const
  {
    typedef typename pythonic::assignable<pythonic::types::empty_list>::type __type0;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::map{})>::type>::type __type1;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::functools::functor::partial{})>::type>::type __type2;
    typedef load_a3m_lambda0 __type3;
    typedef pythonic::types::str __type4;
    typedef long __type5;
    typedef typename pythonic::assignable<pythonic::types::dict<__type4,__type5>>::type __type6;
    typedef decltype(std::declval<__type2>()(std::declval<__type3>(), std::declval<__type6>())) __type7;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::filter{})>::type>::type __type8;
    typedef load_a3m_lambda1 __type9;
    typedef typename pythonic::assignable<pythonic::types::set<__type4>>::type __type10;
    typedef decltype(std::declval<__type2>()(std::declval<__type9>(), std::declval<__type10>())) __type11;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::str::functor::strip{})>::type>::type __type12;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::open{})>::type>::type __type13;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type14;
    typedef typename pythonic::assignable<decltype(std::declval<__type13>()(std::declval<__type14>()))>::type __type15;
    typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type15>::type::iterator>::value_type>::type __type16;
    typedef typename pythonic::assignable<decltype(std::declval<__type12>()(std::declval<__type16>()))>::type __type17;
    typedef decltype(std::declval<__type8>()(std::declval<__type11>(), std::declval<__type17>())) __type18;
    typedef decltype(std::declval<__type1>()(std::declval<__type7>(), std::declval<__type18>())) __type19;
    typedef pythonic::types::list<typename std::remove_reference<__type19>::type> __type20;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::len{})>::type>::type __type21;
    typedef decltype(std::declval<__type12>()(std::declval<__type16>())) __type22;
    typename pythonic::assignable<typename pythonic::assignable<decltype(std::declval<__type21>()(std::declval<__type22>()))>::type>::type seq_length;
    typename pythonic::assignable<decltype(typename pythonic::assignable<pythonic::types::dict<pythonic::types::str,long>>::type{{{ "-", 21L }, { "A", 1L }, { "B", 21L }, { "C", 2L }, { "D", 3L }, { "E", 4L }, { "F", 5L }, { "G", 6L }, { "H", 7L }, { "I", 8L }, { "K", 9L }, { "L", 10L }, { "M", 11L }, { "N", 12L }, { "O", 21L }, { "P", 13L }, { "Q", 14L }, { "R", 15L }, { "S", 16L }, { "T", 17L }, { "V", 18L }, { "W", 19L }, { "Y", 20L }, { "U", 21L }, { "Z", 21L }, { "X", 21L }, { "J", 21L }}})>::type mapping = typename pythonic::assignable<pythonic::types::dict<pythonic::types::str,long>>::type{{{ "-", 21L }, { "A", 1L }, { "B", 21L }, { "C", 2L }, { "D", 3L }, { "E", 4L }, { "F", 5L }, { "G", 6L }, { "H", 7L }, { "I", 8L }, { "K", 9L }, { "L", 10L }, { "M", 11L }, { "N", 12L }, { "O", 21L }, { "P", 13L }, { "Q", 14L }, { "R", 15L }, { "S", 16L }, { "T", 17L }, { "V", 18L }, { "W", 19L }, { "Y", 20L }, { "U", 21L }, { "Z", 21L }, { "X", 21L }, { "J", 21L }}};
    typename pythonic::assignable<decltype(typename pythonic::assignable<pythonic::types::set<pythonic::types::str>>::type{{"d", "k", "q", "n", "w", "l", "h", "x", "y", "c", "s", "g", "o", "a", "u", "z", "j", "b", "e", "f", "r", "i", "v", "m", "t", "p"}})>::type lowercase = typename pythonic::assignable<pythonic::types::set<pythonic::types::str>>::type{{"d", "k", "q", "n", "w", "l", "h", "x", "y", "c", "s", "g", "o", "a", "u", "z", "j", "b", "e", "f", "r", "i", "v", "m", "t", "p"}};
    typename pythonic::assignable<decltype(pythonic::__builtin__::functor::open{}(fasta))>::type f = pythonic::__builtin__::functor::open{}(fasta);
    {
      {
        for (auto&& line: f)
        {
          if (pythonic::__builtin__::str::functor::startswith{}(line, ">"))
          {
            continue;
          }
          seq_length = pythonic::__builtin__::functor::len{}(pythonic::__builtin__::str::functor::strip{}(line));
          goto __no_breaking140501831497768;
        }
      }
      throw pythonic::__builtin__::functor::RuntimeError{}("I cannot find the first sequence");
      __no_breaking140501831497768:;
    }
    pythonic::io::_io::TextIOWrapper::functor::seek{}(f, 0L);
    typename pythonic::assignable<typename __combined<__type0,__type20>::type>::type parsed = pythonic::__builtin__::functor::list{}();
    {
      for (auto&& line_: f)
      {
        if (pythonic::__builtin__::str::functor::startswith{}(line_, ">"))
        {
          continue;
        }
        typename pythonic::assignable<decltype(pythonic::__builtin__::str::functor::strip{}(line_))>::type line__ = pythonic::__builtin__::str::functor::strip{}(line_);
        ;
        if (((pythonic::operator_::div(pythonic::__dispatch__::functor::count{}(line__, "-"), seq_length)) <= max_gap_fraction))
        {
          pythonic::__builtin__::list::functor::append{}(parsed, pythonic::__builtin__::functor::map{}(pythonic::functools::functor::partial{}(load_a3m_lambda0(), mapping), pythonic::__builtin__::functor::filter{}(pythonic::functools::functor::partial{}(load_a3m_lambda1(), lowercase), line__)));
        }
      }
    }
    return pythonic::__builtin__::getattr<pythonic::types::attr::T>(pythonic::numpy::functor::array{}(parsed, pythonic::numpy::functor::int8{}));
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
typename __pythran__load_data::load_a3m::type<pythonic::types::str>::result_type load_a3m0(pythonic::types::str&& fasta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran__load_data::load_a3m()(fasta);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran__load_data::load_a3m::type<pythonic::types::str, double>::result_type load_a3m1(pythonic::types::str&& fasta, double&& max_gap_fraction) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran__load_data::load_a3m()(fasta, max_gap_fraction);
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
__pythran_wrap_load_a3m0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[1+1];
    char const* keywords[] = {"fasta", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "O",
                                     (char**)keywords, &args_obj[0]))
        return nullptr;
    if(is_convertible<pythonic::types::str>(args_obj[0]))
        return to_python(load_a3m0(from_python<pythonic::types::str>(args_obj[0])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_load_a3m1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    char const* keywords[] = {"fasta","max_gap_fraction", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords, &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::str>(args_obj[0]) && is_convertible<double>(args_obj[1]))
        return to_python(load_a3m1(from_python<pythonic::types::str>(args_obj[0]), from_python<double>(args_obj[1])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_load_a3m(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_load_a3m0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_load_a3m1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "load_a3m", "   load_a3m(str)\n   load_a3m(str,float)", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "load_a3m",
    (PyCFunction)__pythran_wrapall_load_a3m,
    METH_VARARGS | METH_KEYWORDS,
    "load alignment with the alphabet used in GaussDCA \n\n   Supported prototypes:\n\n   - load_a3m(str)\n   - load_a3m(str, float)"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_load_data",            /* m_name */
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
PYTHRAN_MODULE_INIT(_load_data)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
__attribute__ ((externally_visible))
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(_load_data)(void) {
    #ifdef PYTHONIC_TYPES_NDARRAY_HPP
        import_array()
    #endif
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("_load_data",
                                         Methods,
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.8.6",
                                      "2018-06-17 17:35:07.551435",
                                      "0129bd3a53dbfa7222ffb5d0209e57369991d14d1e9eaa9d9e8705276534fa98");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);


    PYTHRAN_RETURN;
}

#endif