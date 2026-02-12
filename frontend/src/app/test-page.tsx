export default function TestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-md p-8 space-y-4">
        <h1 className="text-3xl font-bold text-center text-gray-800">Tailwind Test</h1>
        <p className="text-gray-600 text-center">If you see colors and styling, Tailwind is working!</p>
        <div className="flex justify-center">
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-300">
            Styled Button
          </button>
        </div>
      </div>
    </div>
  );
}