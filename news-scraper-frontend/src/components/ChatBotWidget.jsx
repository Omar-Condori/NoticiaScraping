import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import { chatAPI } from '../services/api';
import { useTheme } from '../context/ThemeContext';

export default function ChatBotWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            text: '¡Hola! Soy tu Asistente de Noticias. Puedo responder preguntas basándome en las noticias que has guardado. ¿Qué quieres saber hoy?'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const { theme } = useTheme();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            type: 'user',
            text: inputValue
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await chatAPI.enviarMensaje(inputValue);

            const botMessage = {
                id: Date.now() + 1,
                type: 'bot',
                text: response.data.respuesta,
                fuentes: response.data.fuentes
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error("Error chat:", error);
            const errorMessage = {
                id: Date.now() + 1,
                type: 'bot',
                text: "Lo siento, tuve un problema al procesar tu pregunta. Por favor intenta de nuevo."
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end font-sans">
            {/* Ventana de Chat */}
            {isOpen && (
                <div
                    className={`
            mb-4 w-[350px] h-[500px] rounded-2xl shadow-2xl flex flex-col overflow-hidden border
            ${theme === 'dark'
                            ? 'bg-gray-900 border-gray-700'
                            : 'bg-white border-gray-200'}
            animate-in slide-in-from-bottom-10 fade-in duration-300
          `}
                >
                    {/* Header */}
                    <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                                <Sparkles className="w-4 h-4 text-white" />
                            </div>
                            <div>
                                <h3 className="text-white font-bold text-sm">Asistente IA</h3>
                                <p className="text-blue-100 text-xs flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                                    En línea
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="text-white/80 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-lg"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Mensajes */}
                    <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex items-start gap-2 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div
                                    className={`
                    w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
                    ${msg.type === 'user'
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-purple-500 text-white'}
                  `}
                                >
                                    {msg.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                                </div>

                                <div
                                    className={`
                    max-w-[80%] p-3 rounded-2xl text-sm leading-relaxed
                    ${msg.type === 'user'
                                            ? 'bg-blue-500 text-white rounded-tr-none'
                                            : (theme === 'dark' ? 'bg-gray-800 text-gray-200' : 'bg-white text-gray-700 border border-gray-200 shadow-sm') + ' rounded-tl-none'}
                  `}
                                >
                                    <p>{msg.text}</p>

                                    {/* Fuentes citadas */}
                                    {msg.fuentes && msg.fuentes.length > 0 && (
                                        <div className="mt-2 pt-2 border-t border-white/10">
                                            <p className="text-xs opacity-70 mb-1 font-semibold">Fuentes:</p>
                                            <ul className="list-disc list-inside text-xs opacity-70 space-y-0.5">
                                                {msg.fuentes.map((f, i) => (
                                                    <li key={i} className="truncate">{f}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex items-start gap-2">
                                <div className="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
                                    <Bot className="w-4 h-4" />
                                </div>
                                <div className={`p-3 rounded-2xl rounded-tl-none ${theme === 'dark' ? 'bg-gray-800' : 'bg-white border border-gray-200'}`}>
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form
                        onSubmit={handleSendMessage}
                        className={`p-3 border-t ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}
                    >
                        <div className="relative flex items-center">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder="Pregunta sobre tus noticias..."
                                className={`
                  w-full pl-4 pr-12 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all
                  ${theme === 'dark'
                                        ? 'bg-gray-900 text-white placeholder-gray-500 border border-gray-700'
                                        : 'bg-gray-100 text-gray-900 placeholder-gray-500 border-transparent'}
                `}
                                disabled={isLoading}
                            />
                            <button
                                type="submit"
                                disabled={!inputValue.trim() || isLoading}
                                className={`
                  absolute right-2 p-2 rounded-lg transition-all
                  ${!inputValue.trim() || isLoading
                                        ? 'text-gray-400 cursor-not-allowed'
                                        : 'bg-purple-500 text-white hover:bg-purple-600 shadow-lg hover:shadow-purple-500/25'}
                `}
                            >
                                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Botón Flotante */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`
          group relative flex items-center justify-center w-14 h-14 rounded-full shadow-lg transition-all duration-300 hover:scale-110
          ${isOpen
                        ? 'bg-gray-700 text-white rotate-90'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-purple-500/50'}
        `}
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}

                {/* Badge de notificación (opcional) */}
                {!isOpen && (
                    <span className="absolute top-0 right-0 flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                )}
            </button>
        </div>
    );
}
