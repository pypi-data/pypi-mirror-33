
	
	template<class T, T v>
	struct integral_constant {
		static constexpr T value = v;
		typedef T value_type;
		typedef integral_constant type;
		constexpr operator value_type() { return value; }
		constexpr value_type operator()() const { return value; } 
	};
	
	template <bool B>
	using bool_constant = integral_constant<bool, B>;
	
	using true_type = bool_constant<true>;

	using false_type = bool_constant<false>;
	
	
	// Types small_ and big_ are guaranteed such that sizeof(small_) <	sizeof(big_)
	struct small_	{char dummy[1];};
	struct big_ 	{char dummy[2];};
	typedef small_ yes_tag;
	typedef big_ no_tag;

	
   /**
   *  @brief  Utility to simplify expressions used in unevaluated operands
   *  @ingroup utilities
   */
   template<typename _Tp>
   typename add_rvalue_reference<_Tp>::type declval() noexcept;


	template<bool B, class T = void>
	struct enable_if {};
	 
	template<class T>
	struct enable_if<true, T> { typedef T type; };

	template<bool B, class T>
	using enable_if_t = typename enable_if<B,T>::type;

	template <class...>
	using void_t = void;
	
	template <class, class T, class... Args>
	struct is_constructible_ : std::false_type {};
	
	template <class T, class... Args>
	struct is_constructible_<
	    void_t<decltype(T(std::declval<Args>()...))>,
	T, Args...> : std::true_type {};
	
	template <class T, class... Args>
	using is_constructible = is_constructible_<void_t<>, T, Args...>;