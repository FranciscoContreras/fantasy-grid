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
    <div className="min-h-screen flex items-center justify-center bg-black p-4 font-body">
      <Card className="w-full max-w-md p-8 bg-gray-900 text-white border-4 border-gray-700">
        <div className="text-center mb-8 border-b-2 border-gray-600 pb-6">
          <h1 className="text-4xl font-script text-white mb-4">
            Pilon
          </h1>
          <p className="text-gray-300 font-display uppercase tracking-[0.2em] text-sm">
            {isLogin ? 'Championship Login' : 'Join The Champions'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-display uppercase tracking-[0.2em] text-gray-400 mb-3">
                  First Name
                </label>
                <Input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  placeholder="JOHN"
                  className="bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white placeholder:text-gray-500 placeholder:uppercase placeholder:tracking-wider"
                />
              </div>
              <div>
                <label className="block text-sm font-display uppercase tracking-[0.2em] text-gray-400 mb-3">
                  Last Name
                </label>
                <Input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  placeholder="DOE"
                  className="bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white placeholder:text-gray-500 placeholder:uppercase placeholder:tracking-wider"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-display uppercase tracking-[0.2em] text-gray-400 mb-3">
              {isLogin ? 'Email or Username' : 'Email'}
            </label>
            <Input
              type={isLogin ? 'text' : 'email'}
              required
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder={isLogin ? 'EMAIL@CHAMPION.COM OR USERNAME' : 'EMAIL@CHAMPION.COM'}
              className="bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white placeholder:text-gray-500 placeholder:uppercase placeholder:tracking-wider"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-display uppercase tracking-[0.2em] text-gray-400 mb-3">
                Username
              </label>
              <Input
                type="text"
                required
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                placeholder="CHAMPION"
                minLength={3}
                className="bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white placeholder:text-gray-500 placeholder:uppercase placeholder:tracking-wider"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-display uppercase tracking-[0.2em] text-gray-400 mb-3">
              Password
            </label>
            <Input
              type="password"
              required
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              placeholder="••••••••"
              minLength={8}
              className="bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white placeholder:text-gray-500"
            />
          </div>

          {error && (
            <div className="p-4 bg-red-900 border-2 border-red-700 text-center">
              <p className="text-sm text-red-300 font-display uppercase tracking-wider">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full bg-white text-black hover:bg-gray-100 font-display uppercase tracking-[0.2em] text-lg py-6 border-2 border-white disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            disabled={loading}
          >
            {loading ? 'PROCESSING...' : isLogin ? 'ENTER CHAMPIONSHIP' : 'JOIN CHAMPIONS'}
          </Button>
        </form>

        <div className="mt-8 text-center border-t-2 border-gray-600 pt-6">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-sm text-gray-300 hover:text-white font-display uppercase tracking-[0.2em] transition-colors"
          >
            {isLogin
              ? "NEW CHAMPION? JOIN HERE"
              : 'CHAMPION RETURNING? SIGN IN'}
          </button>
        </div>
      </Card>
    </div>
  );
}
