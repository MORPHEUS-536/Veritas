import React, { useState } from 'react';
import FormInput from './FormInput';
import AnimatedBackground from './AnimatedBackground';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';

/**
 * LoginPage Component
 * Professional split-screen login page with animated hero section
 * Color Scheme: Deep Indigo (#4F46E5), Emerald Green (#10B981), Light Slate (#F8FAFC)
 */
const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validation
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address');
      setIsLoading(false);
      return;
    }

    // Simulated API call
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Login attempt:', { ...formData, rememberMe });
      alert('Login successful! (Simulated)');
      setFormData({ email: '', password: '' });
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    console.log(`${provider} login initiated`);
    alert(`${provider} login would be handled here`);
  };

  return (
    <div className="min-h-screen bg-slate-light flex overflow-hidden">
      {/* Left Section - Hero with Animated Background */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 via-primary-500 to-primary-700 relative overflow-hidden justify-center items-center">
        {/* Animated Background */}
        <AnimatedBackground />

        {/* Hero Content */}
        <div className="relative z-10 px-12 text-white text-center max-w-md">
          <div className="mb-8">
            <div className="w-16 h-16 bg-success rounded-full flex items-center justify-center mx-auto mb-6 animate-float">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v2h8v-2zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-2a4 4 0 00-8 0v2a2 2 0 002 2h4a2 2 0 002-2z" />
              </svg>
            </div>
          </div>
          <h2 className="text-4xl font-bold mb-4">Welcome Back</h2>
          <p className="text-lg text-primary-100 mb-8">
            Join thousands of learners transforming their education journey. Access personalized learning paths and track your growth.
          </p>
          <div className="flex gap-4 justify-center">
            <div className="flex flex-col items-center">
              <span className="text-3xl font-bold">50K+</span>
              <span className="text-sm text-primary-100">Active Learners</span>
            </div>
            <div className="w-px bg-primary-400"></div>
            <div className="flex flex-col items-center">
              <span className="text-3xl font-bold">4.9★</span>
              <span className="text-sm text-primary-100">User Rating</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Section - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 sm:px-8 lg:px-12 py-12">
        <div className="w-full max-w-md">
          {/* Logo / Branding */}
          <div className="mb-10 text-center lg:text-left">
            <h1 className="text-3xl font-bold text-primary-600 mb-2">Veritas</h1>
            <p className="text-gray-600">Sign in to your account</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <FormInput
              label="Email Address"
              type="email"
              name="email"
              placeholder=""
              value={formData.email}
              onChange={handleInputChange}
              required
              icon={Mail}
            />

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder=""
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 pl-11 rounded-lg border-2 border-gray-200 hover:border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all duration-200 text-gray-900 placeholder-gray-400 font-medium"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 text-primary-500 rounded border-gray-300 focus:ring-primary-500 cursor-pointer"
                />
                <span className="ml-2 text-sm text-gray-600">Remember me</span>
              </label>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  alert('Forgot password functionality would go here');
                }}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors"
              >
                Forgot password?
              </a>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                backgroundColor: isLoading ? '#e0d7ff' : '#4F46E5',
              }}
              className={`w-full py-3 rounded-lg font-bold text-white transition-all duration-200 ${
                isLoading
                  ? 'cursor-not-allowed opacity-75'
                  : 'hover:opacity-90 active:scale-95'
              } shadow-lg hover:shadow-xl`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Signing in...
                </span>
              ) : (
                'Login'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-slate-light text-gray-500">Or continue with</span>
            </div>
          </div>

          {/* Social Login Buttons */}
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => handleSocialLogin('Google')}
              className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all duration-200 font-medium text-gray-700 hover:text-primary-600"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>
            <button
              type="button"
              onClick={() => handleSocialLogin('GitHub')}
              className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all duration-200 font-medium text-gray-700 hover:text-primary-600"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v 3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </button>
          </div>

          {/* Sign Up Link */}
          <p className="text-center text-gray-600 mt-8">
            Don't have an account?{' '}
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                alert('Sign up page would go here');
              }}
              className="text-primary-600 hover:text-primary-700 font-bold transition-colors"
            >
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
