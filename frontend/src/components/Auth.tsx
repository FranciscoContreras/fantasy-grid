import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { login, register } from '../lib/api';

interface AuthProps {
  onAuthSuccess: (isNewUser?: boolean) => void;
}

export function Auth({ onAuthSuccess }: AuthProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await login(formData.email || formData.username, formData.password);
        onAuthSuccess(false);
      } else {
        await register({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          first_name: formData.first_name,
          last_name: formData.last_name,
        });
        onAuthSuccess(true); // New user, trigger onboarding
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6 font-system">
      {/* Subtle Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-gray-100/30 to-gray-200/30 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-r from-gray-100/20 to-gray-200/20 rounded-full blur-3xl"></div>
      </div>

      <div className="relative w-full max-w-md bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-logo text-gray-900 mb-3">
            Pilon
          </h1>
          <p className="text-gray-600 font-medium text-sm">
            {isLogin ? 'Welcome back' : 'Join the platform'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <Input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  placeholder="John"
                  className="border-gray-300 text-gray-900 font-medium p-3 focus:border-gray-400 focus:ring-1 focus:ring-gray-400 placeholder:text-gray-400 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <Input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  placeholder="Doe"
                  className="border-gray-300 text-gray-900 font-medium p-3 focus:border-gray-400 focus:ring-1 focus:ring-gray-400 placeholder:text-gray-400 rounded-lg"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isLogin ? 'Email or Username' : 'Email'}
            </label>
            <Input
              type={isLogin ? 'text' : 'email'}
              required
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder={isLogin ? 'email@example.com or username' : 'email@example.com'}
              className="border-gray-300 text-gray-900 font-medium p-3 focus:border-gray-400 focus:ring-1 focus:ring-gray-400 placeholder:text-gray-400 rounded-lg"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <Input
                type="text"
                required
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                placeholder="username"
                minLength={3}
                className="border-gray-300 text-gray-900 font-medium p-3 focus:border-gray-400 focus:ring-1 focus:ring-gray-400 placeholder:text-gray-400 rounded-lg"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <Input
              type="password"
              required
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              placeholder="••••••••"
              minLength={8}
              className="border-gray-300 text-gray-900 font-medium p-3 focus:border-gray-400 focus:ring-1 focus:ring-gray-400 placeholder:text-gray-400 rounded-lg"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg text-center">
              <p className="text-sm text-red-600 font-medium">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full bg-gray-900 text-white hover:bg-gray-800 font-semibold py-3 rounded-lg border-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
            disabled={loading}
          >
            {loading ? 'Loading...' : isLogin ? 'Sign In' : 'Create Account'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            {isLogin
              ? "Don't have an account? Sign up"
              : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
}
