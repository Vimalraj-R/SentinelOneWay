import { MessageSquare, Plus, User, Clock } from 'lucide-react';
import { useState } from 'react';

export default function AnalystNotes({ notes: initialNotes }) {
  const [notes, setNotes] = useState(initialNotes);
  const [newNote, setNewNote] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddNote = () => {
    if (newNote.trim()) {
      const note = {
        id: notes.length + 1,
        author: 'current-analyst',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        note: newNote
      };
      setNotes([...notes, note]);
      setNewNote('');
      setIsAdding(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    // If it's already formatted, return as is
    if (typeof timestamp === 'string' && timestamp.includes(':')) {
      return timestamp;
    }
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-green-400" />
          <h2 className="text-xl font-semibold text-white">Analyst Notes</h2>
        </div>
        {!isAdding && (
          <button
            onClick={() => setIsAdding(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Note
          </button>
        )}
      </div>

      {/* Add Note Form */}
      {isAdding && (
        <div className="mb-4 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Enter your note..."
            className="w-full bg-gray-900 text-white border border-gray-700 rounded-lg p-3 mb-3 focus:outline-none focus:border-green-500 resize-none"
            rows="3"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddNote}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Save Note
            </button>
            <button
              onClick={() => {
                setIsAdding(false);
                setNewNote('');
              }}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Notes List */}
      <div className="space-y-3">
        {notes.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No notes yet</p>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300 text-sm font-medium">{note.author}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-3 h-3 text-gray-500" />
                  <span className="text-gray-500 text-xs">{formatTimestamp(note.timestamp)}</span>
                </div>
              </div>
              <p className="text-gray-200 text-sm leading-relaxed">{note.note}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
