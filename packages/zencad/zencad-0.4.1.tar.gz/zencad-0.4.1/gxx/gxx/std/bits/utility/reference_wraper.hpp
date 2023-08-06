template< class T >
T* addressof(T& arg) 
{
    return reinterpret_cast<T*>(
               &const_cast<char&>(
                  reinterpret_cast<const volatile char&>(arg)));
}

namespace detail {
template <class F, class... Args>
inline auto INVOKE(F&& f, Args&&... args) ->
    decltype(forward<F>(f)(forward<Args>(args)...)) {
      return forward<F>(f)(forward<Args>(args)...);
}
 
template <class Base, class T, class Derived>
inline auto INVOKE(T Base::*pmd, Derived&& ref) ->
    decltype(forward<Derived>(ref).*pmd) {
      return forward<Derived>(ref).*pmd;
}
 
template <class PMD, class Pointer>
inline auto INVOKE(PMD&& pmd, Pointer&& ptr) ->
    decltype((*forward<Pointer>(ptr)).*forward<PMD>(pmd)) {
      return (*forward<Pointer>(ptr)).*forward<PMD>(pmd);
}
 
template <class Base, class T, class Derived, class... Args>
inline auto INVOKE(T Base::*pmf, Derived&& ref, Args&&... args) ->
    decltype((forward<Derived>(ref).*pmf)(forward<Args>(args)...)) {
      return (forward<Derived>(ref).*pmf)(forward<Args>(args)...);
}
 
template <class PMF, class Pointer, class... Args>
inline auto INVOKE(PMF&& pmf, Pointer&& ptr, Args&&... args) ->
    decltype(((*forward<Pointer>(ptr)).*forward<PMF>(pmf))(forward<Args>(args)...)) {
      return ((*forward<Pointer>(ptr)).*forward<PMF>(pmf))(forward<Args>(args)...);
}
} // namespace detail
 
// Подходящая для C++14 реализация (также подходит для реализации C++11):
namespace detail {
template <typename, typename = void>
struct result_of {};
template <typename F, typename...Args>
struct result_of<F(Args...),
                 decltype(void(detail::INVOKE(std::declval<F>(), std::declval<Args>()...)))> {
    using type = decltype(detail::INVOKE(std::declval<F>(), std::declval<Args>()...));
};
} // namespace detail
 
template <class> struct result_of;
template <class F, class... ArgTypes>
struct result_of<F(ArgTypes...)> : detail::result_of<F(ArgTypes...)> {};

template<typename Func, typename ... Args>
auto invoke(Func&& func, Args ... args) -> decltype(func(args ...)) {
  return func(args ...); 
}

template <class T>
class reference_wrapper {
public:
  // types
  typedef T type;
 
  // construct/copy/destroy
  reference_wrapper(T& ref) noexcept : _ptr(std::addressof(ref)) {}
  reference_wrapper(T&&) = delete;
  reference_wrapper(const reference_wrapper&) noexcept = default;
 
  // assignment
  reference_wrapper& operator=(const reference_wrapper& x) noexcept = default;
 
  // access
  operator T& () const noexcept { return *_ptr; }
  T& get() const noexcept { return *_ptr; }
 
  template< class... ArgTypes >
  typename std::result_of<T&(ArgTypes&&...)>::type
    operator() ( ArgTypes&&... args ) const {
    return std::invoke(get(), std::forward<ArgTypes>(args)...);
  }
 
private:
  T* _ptr;
};
