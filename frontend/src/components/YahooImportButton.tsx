/**
 * Yahoo Fantasy Roster Import Button
 *
 * Simple button component to initiate Yahoo OAuth flow
 */

interface YahooImportButtonProps {
  className?: string;
}

export const YahooImportButton = ({ className = '' }: YahooImportButtonProps) => {
  const handleYahooImport = () => {
    // Get JWT token from localStorage (stored as 'auth_token')
    const token = localStorage.getItem('auth_token');

    if (!token) {
      alert('Please log in first to import from Yahoo');
      return;
    }

    // Redirect to Yahoo OAuth endpoint with token as query parameter
    window.location.href = `/api/yahoo/auth?token=${token}`;
  };

  return (
    <button
      onClick={handleYahooImport}
      className={`
        flex items-center gap-2 px-4 py-2
        bg-purple-600 hover:bg-purple-700
        text-white font-medium rounded-lg
        transition-colors duration-200
        ${className}
      `.trim()}
    >
      <svg
        className="w-5 h-5"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      Import from Yahoo Fantasy
    </button>
  );
};
