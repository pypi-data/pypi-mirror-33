

	
	
	
//is_same cравнивает два типа, а не одинаковые ли они
template<class T, class U> 	struct is_same 					: std::false_type 	{};
template<class T> 			struct is_same<T, T> 			: std::true_type 	{};

//is_reference
template<class T>			struct is_reference 			: std::false_type 	{};
template<class T>			struct is_reference<T&> 		: std::true_type 	{};
template<class T>			struct is_reference<T&&> 		: std::true_type 	{};

//is_rvalue_reference
template<class T>			struct is_rvalue_reference 				: std::false_type 	{};
template<class T>			struct is_rvalue_reference<T&&> 		: std::true_type 	{};

//is_lvalue_reference
template<class T>			struct is_lvalue_reference 				: std::false_type 	{};
template<class T>			struct is_lvalue_reference<T&> 			: std::true_type 	{};

//is_pointer
template< class T > struct is_pointer_helper     : std::false_type {};
template< class T > struct is_pointer_helper<T*> : std::true_type {};
template< class T > struct is_pointer : is_pointer_helper<typename std::remove_cv<T>::type> {};

//is_const
template<class T> 			struct is_const 				: std::false_type 	{};
template<class T> 			struct is_const<const T> 		: std::true_type 	{};

//is_volatile
template<class T> 			struct is_volatile 				: std::false_type 	{};
template<class T> 			struct is_volatile<volatile T> 	: std::true_type 	{};

//is_integral
template <class T> 			struct is_integral 						: false_type { };
template<> 					struct is_integral<bool> 				: true_type { };
template<> 					struct is_integral<char> 				: true_type { };
template<>					struct is_integral<unsigned char> 		: true_type { };
template<> 					struct is_integral<signed char> 		: true_type { };
template<> 					struct is_integral<wchar_t> 			: true_type { };
template<> 					struct is_integral<short> 				: true_type { };
template<> 					struct is_integral<unsigned short> 		: true_type { };
template<> 					struct is_integral<int> 				: true_type { };
template<> 					struct is_integral<unsigned int> 		: true_type { };
template<> 					struct is_integral<long> 				: true_type { };
template<> 					struct is_integral<unsigned long> 		: true_type { };
template<> 					struct is_integral<long long> 			: true_type { };
template<> 					struct is_integral<unsigned long long> 	: true_type { };

//is_signed
template <class T>      struct is_signed            : false_type { };
template<>          struct is_signed<bool>        : false_type { };
template<>          struct is_signed<char>        : true_type { };
template<>          struct is_signed<unsigned char>     : false_type { };
template<>          struct is_signed<signed char>     : true_type { };
template<>          struct is_signed<wchar_t>       : true_type { };
template<>          struct is_signed<short>         : true_type { };
template<>          struct is_signed<unsigned short>    : false_type { };
template<>          struct is_signed<int>         : true_type { };
template<>          struct is_signed<unsigned int>    : false_type { };
template<>          struct is_signed<long>        : true_type { };
template<>          struct is_signed<unsigned long>     : false_type { };
template<>          struct is_signed<long long>       : true_type { };
template<>          struct is_signed<unsigned long long>  : false_type { };


// is_floating_point 
template <class T> 			struct is_floating_point 				: false_type { };
template<> 					struct is_floating_point<float> 		: true_type { };
template<> 					struct is_floating_point<double> 		: true_type { };
template<> 					struct is_floating_point<long double> 	: true_type { };

template<class T>			struct is_arithmetic : std::bool_constant<
                          std::is_integral<T>::value ||
                                 std::is_floating_point<T>::value> {};

template< class T >
struct is_void : std::is_same<void, typename std::remove_cv<T>::type> {};
											  
template<class T>
struct is_array : std::false_type {};
 
template<class T>
struct is_array<T[]> : std::true_type {};
 
template<class T, size_t N>
struct is_array<T[N]> : std::true_type {};											  
											  
											  
											  
template< class T >
struct decay {
private:
    typedef typename std::remove_reference<T>::type U;
public:
    typedef typename std::conditional< 
        std::is_array<U>::value,
        typename std::remove_extent<U>::type*,
        typename std::conditional< 
            std::is_function<U>::value,
            typename std::add_pointer<U>::type,
            typename std::remove_cv<U>::type
        >::type
    >::type type;
};  
											  
											  
											  
											  
											  
											  
										  
namespace internal {

//Магия: т.к. компилятор предпочитает не использовать функции с переменным числом параметров,
//он не станет выбирать tester(void (U::*)()) только в случае, когда U::* вообще невозможен.
//то есть U не структуроподобен.
template <class T> struct is_class_or_union {
  template <class U> static small_ 	tester(void (U::*)());
  template <class U> static big_ 	tester(...);
  static const bool value = sizeof(tester<T>(0)) == sizeof(small_);
};

// is_convertible chokes if the first argument is an array. That's why
// we use add_reference here.
template <bool NotUnum, class T> struct is_enum_impl
    : is_convertible<typename std::add_reference<T>::type, int> { };

template <class T> struct is_enum_impl<true, T> : false_type { };
  
}// namespace internal
				


// Specified by TR1 [4.5.1] primary type categories.

// Implementation note:
//
// Each type is either void, integral, floating point, array, pointer,
// reference, member object pointer, member function pointer, enum,
// union or class. Out of these, only integral, floating point, reference,
// class and enum types are potentially convertible to int. Therefore,
// if a type is not a reference, integral, floating point or class and
// is convertible to int, it's a enum.
//
// Is-convertible-to-int check is done only if all other checks pass,
// because it can't be used with some types (e.g. void or classes with
// inaccessible conversion operators).
template <class T> struct is_enum
    : internal::is_enum_impl<
          is_same<T, void>::value ||
              is_integral<T>::value ||
              is_floating_point<T>::value ||
              is_reference<T>::value ||
              internal::is_class_or_union<T>::value,
          T> { };

template <class T> struct is_enum<const T> : is_enum<T> { };
template <class T> struct is_enum<volatile T> : is_enum<T> { };
template <class T> struct is_enum<const volatile T> : is_enum<T> { };


// We can't get is_pod right without compiler help, so fail conservatively.
// We will assume it's false except for arithmetic types, enumerations,
// pointers and const versions thereof. Note that std::pair is not a POD.
template <class T> struct is_pod
 : integral_constant<bool, (is_integral<T>::value ||
                            is_floating_point<T>::value ||
                            is_enum<T>::value ||
                            is_pointer<T>::value)> { };
template <class T> struct is_pod<const T> : is_pod<T> { };


// We can't get has_trivial_constructor right without compiler help, so
// fail conservatively. We will assume it's false except for: (1) types
// for which is_pod is true. (2) std::pair of types with trivial
// constructors. (3) array of a type with a trivial constructor.
// (4) const versions thereof.
template <class T> struct has_trivial_constructor : is_pod<T> { };
template <class T, class U> struct has_trivial_constructor<std::pair<T, U> >
  : integral_constant<bool,
                      (has_trivial_constructor<T>::value &&
                       has_trivial_constructor<U>::value)> { };
template <class A, int N> struct has_trivial_constructor<A[N]>
  : has_trivial_constructor<A> { };
template <class T> struct has_trivial_constructor<const T>
  : has_trivial_constructor<T> { };

// We can't get has_trivial_copy right without compiler help, so fail
// conservatively. We will assume it's false except for: (1) types
// for which is_pod is true. (2) std::pair of types with trivial copy
// constructors. (3) array of a type with a trivial copy constructor.
// (4) const versions thereof.
template <class T> struct has_trivial_copy : is_pod<T> { };
template <class T, class U> struct has_trivial_copy<std::pair<T, U> >
  : integral_constant<bool,
                      (has_trivial_copy<T>::value &&
                       has_trivial_copy<U>::value)> { };
template <class A, int N> struct has_trivial_copy<A[N]>
  : has_trivial_copy<A> { };
template <class T> struct has_trivial_copy<const T> : has_trivial_copy<T> { };

// We can't get has_trivial_assign right without compiler help, so fail
// conservatively. We will assume it's false except for: (1) types
// for which is_pod is true. (2) std::pair of types with trivial copy
// constructors. (3) array of a type with a trivial assign constructor.
template <class T> struct has_trivial_assign : is_pod<T> { };
template <class T, class U> struct has_trivial_assign<std::pair<T, U> >
  : integral_constant<bool,
                      (has_trivial_assign<T>::value &&
                       has_trivial_assign<U>::value)> { };
template <class A, int N> struct has_trivial_assign<A[N]>
  : has_trivial_assign<A> { };

// We can't get has_trivial_destructor right without compiler help, so
// fail conservatively. We will assume it's false except for: (1) types
// for which is_pod is true. (2) std::pair of types with trivial
// destructors. (3) array of a type with a trivial destructor.
// (4) const versions thereof.
template <class T> struct has_trivial_destructor : is_pod<T> { };
template <class T, class U> struct has_trivial_destructor<std::pair<T, U> >
  : integral_constant<bool,
                      (has_trivial_destructor<T>::value &&
                       has_trivial_destructor<U>::value)> { };
template <class A, int N> struct has_trivial_destructor<A[N]>
  : has_trivial_destructor<A> { };
template <class T> struct has_trivial_destructor<const T>
  : has_trivial_destructor<T> { };



namespace internal {
template <typename From, typename To>
struct ConvertHelper {
  static small_ Test(To);
  static big_ Test(...);
  static From Create();
};
}// namespace internal

//is_convertible
// Наследует от true_type если From можно сконвертировать в To, иначе от false_type.
template <typename From, typename To>
struct is_convertible : bool_constant
<sizeof(internal::ConvertHelper<From, To>::
Test(internal::ConvertHelper<From, To>::Create())) == sizeof(small_)> {};









// primary template
template<class>
struct is_function : std::false_type { };
 
// specialization for regular functions
template<class Ret, class... Args>
struct is_function<Ret(Args...)> : std::true_type {};
 
// specialization for variadic functions such as std::printf
template<class Ret, class... Args>
struct is_function<Ret(Args......)> : std::true_type {};
 
// specialization for function types that have cv-qualifiers
template<class Ret, class... Args>
struct is_function<Ret(Args...)const> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)volatile> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)const volatile> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)const> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)volatile> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)const volatile> : std::true_type {};
 
// specialization for function types that have ref-qualifiers
template<class Ret, class... Args>
struct is_function<Ret(Args...) &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)const &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)volatile &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)const volatile &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......) &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)const &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)volatile &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)const volatile &> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...) &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)const &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)volatile &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args...)const volatile &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......) &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)const &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)volatile &&> : std::true_type {};
template<class Ret, class... Args>
struct is_function<Ret(Args......)const volatile &&> : std::true_type {};


template< class T >
struct is_member_pointer_helper         : std::false_type {};
 
template< class T, class U >
struct is_member_pointer_helper<T U::*> : std::true_type {};
 
template< class T >
struct is_member_pointer : 
    is_member_pointer_helper<typename std::remove_cv<T>::type> {};

template<class T>
struct is_member_object_pointer : std::integral_constant<
                                      bool,
                                      std::is_member_pointer<T>::value &&
                                      !std::is_member_function_pointer<T>::value
                                  > {};
								  
template< class T >
struct is_member_function_pointer_helper : std::false_type {};
 
template< class T, class U>
struct is_member_function_pointer_helper<T U::*> : std::is_function<T> {};
 
template< class T >
struct is_member_function_pointer : is_member_function_pointer_helper<
                                        typename std::remove_cv<T>::type
                                    > {};
									
template< class T>
struct is_object : std::bool_constant<
                     std::is_scalar<T>::value ||
                     std::is_array<T>::value  ||
                     std::internal::is_class_or_union<T>::value > {};

					 
template< class T > struct is_null_pointer : is_same<typename std::remove_cv<T>::type, nullptr_t> {};
					 
template< class T >
struct is_scalar : std::bool_constant<
                     std::is_arithmetic<T>::value     ||
                     std::is_enum<T>::value           ||
                     std::is_pointer<T>::value        ||
                     std::is_member_pointer<T>::value ||
                     std::is_null_pointer<T>::value > {};

template< class T >
struct is_fundamental
  : std::integral_constant<
        bool,
        std::is_arithmetic<T>::value ||
        std::is_void<T>::value  ||
        std::is_same<nullptr_t, typename std::remove_cv<T>::type>::value
> {};

template< class T >
struct is_compound : std::integral_constant<bool, !std::is_fundamental<T>::value> {};


template< class T >
struct alignment_of : std::integral_constant<
                          std::size_t,
                          alignof(T)
                       > {};
											  
template<class T>
struct rank : public std::integral_constant<std::size_t, 0> {};
 
template<class T>
struct rank<T[]> : public std::integral_constant<std::size_t, rank<T>::value + 1> {};
 
template<class T, std::size_t N>
struct rank<T[N]> : public std::integral_constant<std::size_t, rank<T>::value + 1> {};


template<class T, unsigned N = 0>
struct extent : std::integral_constant<std::size_t, 0> {};
 
template<class T>
struct extent<T[], 0> : std::integral_constant<std::size_t, 0> {};
 
template<class T, unsigned N>
struct extent<T[], N> : std::integral_constant<std::size_t, std::extent<T, N-1>::value> {};
 
template<class T, std::size_t N>
struct extent<T[N], 0> : std::integral_constant<std::size_t, N> {};
 
template<class T, std::size_t I, unsigned N>
struct extent<T[I], N> : std::integral_constant<std::size_t, std::extent<T, N-1>::value> {};
