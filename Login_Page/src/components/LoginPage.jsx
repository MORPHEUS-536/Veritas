import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FormInput from './FormInput';
import AnimatedBackground from './AnimatedBackground';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';

/**
 * LoginPage Component
 * Professional split-screen login page with animated hero section
 * Color Scheme: Deep Indigo (#4F46E5), Emerald Green (#10B981), Light Slate (#F8FAFC)
 */
const LoginPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
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

      // Teacher account credentials
      const teacherEmail = 'Vteacher@gmail.com';
      const teacherPassword = '123';

      // Student account credentials
      const studentEmail = 'veritas@gmail.com';
      const studentPassword = '123';

      if (formData.email === teacherEmail && formData.password === teacherPassword) {
        console.log('Teacher login successful:', formData.email);
        setFormData({ email: '', password: '' });
        // Redirect to Teacher Dashboard on port 1575
        setTimeout(() => {
          window.location.href = 'http://localhost:1575';
        }, 500);
      } else if (formData.email === studentEmail && formData.password === studentPassword) {
        console.log('Student login successful:', formData.email);
        setFormData({ email: '', password: '' });
        // Redirect to Student Portal on port 1574
        setTimeout(() => {
          window.location.href = 'http://localhost:1574';
        }, 500);
      } else {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
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

          {/* Test Account Hint */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-2">
            <p className="text-blue-700 text-xs font-medium">
              💡 Student Account: veritas@gmail.com / 123
            </p>
            <p className="text-blue-700 text-xs font-medium">
              👨‍🏫 Teacher Account: Vteacher@gmail.com / 123
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6 pb-20">
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

            <div className="mb-12">
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

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                backgroundColor: isLoading ? '#e0d7ff' : '#4F46E5',
              }}
              className={` mt-8 mb-16 w-full py-3 rounded-lg font-bold text-white transition-all duration-200 ${isLoading
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
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
