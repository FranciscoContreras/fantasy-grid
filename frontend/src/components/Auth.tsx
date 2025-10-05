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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6 font-system">
      {/* Monochromatic Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-white/3 to-white/8 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-r from-white/2 to-white/6 rounded-full blur-3xl"></div>
      </div>

      <div className="relative w-full max-w-md glass-card p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-logo text-white mb-3">
            Pilon
          </h1>
          <p className="text-white/60 font-medium text-sm">
            {isLogin ? 'Welcome back' : 'Join the platform'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  First Name
                </label>
                <Input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  placeholder="John"
                  className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/40"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Last Name
                </label>
                <Input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  placeholder="Doe"
                  className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/40"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              {isLogin ? 'Email or Username' : 'Email'}
            </label>
            <Input
              type={isLogin ? 'text' : 'email'}
              required
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder={isLogin ? 'email@example.com or username' : 'email@example.com'}
              className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/40"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Username
              </label>
              <Input
                type="text"
                required
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                placeholder="username"
                minLength={3}
                className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/40"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Password
            </label>
            <Input
              type="password"
              required
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              placeholder="••••••••"
              minLength={8}
              className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/50"
            />
          </div>

          {error && (
            <div className="glass-dark p-4 rounded-xl text-center">
              <p className="text-sm text-red-300 font-medium">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full glass bg-white/20 text-white hover:bg-white/30 font-semibold py-3 rounded-xl border-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
            className="text-sm text-white/60 hover:text-white font-medium transition-colors"
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
