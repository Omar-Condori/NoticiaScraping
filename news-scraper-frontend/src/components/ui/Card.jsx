import { ExternalLink, Calendar, Tag, Image as ImageIcon } from 'lucide-react';

export default function Card({ noticia, onClick }) {
  // ← MEJORADO: Función para formatear fecha (prioriza fecha_publicacion)
  const formatearFecha = (fechaPublicacion, fechaScraping) => {
    const fecha = fechaPublicacion || fechaScraping;
    if (!fecha) return 'Fecha desconocida';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <article
      onClick={() => onClick && onClick(noticia)}
      className="bg-light-card dark:bg-dark-card border border-light-border dark:border-dark-border rounded-xl overflow-hidden hover:border-accent-primary/50 transition-all duration-300 hover:shadow-xl hover:shadow-accent-primary/10 cursor-pointer group"
    >
      {/* ← MEJORADO: Sección de imagen con mejor manejo de errores */}
      {noticia.imagen_url && noticia.imagen_url.trim() !== '' ? (
        <div className="relative h-48 bg-light-hover dark:bg-dark-hover overflow-hidden">
          <img
            src={noticia.imagen_url}
            alt={noticia.titulo || 'Imagen de noticia'}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
            onError={(e) => {
              // Si la imagen falla al cargar, ocultar y mostrar placeholder
              const img = e.target;
              const placeholder = img.nextElementSibling;
              if (img) img.style.display = 'none';
              if (placeholder) placeholder.style.display = 'flex';
            }}
          />
          {/* Placeholder si no carga la imagen */}
          <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center hidden">
            <ImageIcon className="w-12 h-12 text-gray-400 dark:text-gray-600" />
          </div>

          {/* ← NUEVO: Badge de categoría sobre la imagen */}
          {noticia.categoria && (
            <div className="absolute top-3 left-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-accent-primary/90 backdrop-blur-sm text-white text-xs font-medium rounded-full">
                <Tag className="w-3 h-3" />
                {noticia.categoria}
              </span>
            </div>
          )}
        </div>
      ) : (
        // Placeholder cuando no hay imagen
        <div className="relative h-48 bg-gradient-to-br from-accent-primary/10 to-accent-secondary/10 flex items-center justify-center group-hover:scale-105 transition-transform duration-500">
          <ImageIcon className="w-12 h-12 text-gray-400 dark:text-gray-600" />
          {noticia.categoria && (
            <div className="absolute top-3 left-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-accent-primary/90 backdrop-blur-sm text-white text-xs font-medium rounded-full">
                <Tag className="w-3 h-3" />
                {noticia.categoria}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Contenido de la tarjeta */}
      <div className="p-5">
        {/* Título */}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 line-clamp-2 group-hover:text-accent-primary transition-colors">
          {noticia.titulo}
        </h3>

        {/* Resumen */}
        {noticia.resumen && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
            {noticia.resumen}
          </p>
        )}

        {/* Footer con metadata */}
        <div className="flex items-center justify-between pt-4 border-t border-light-border dark:border-dark-border">
          {/* Fuente y fecha */}
          <div className="flex flex-col gap-1">
            <span className="text-xs font-medium text-accent-primary">
              {noticia.fuente || 'Fuente desconocida'}
            </span>
            <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
              <Calendar className="w-3 h-3" />
              {formatearFecha(noticia.fecha_publicacion, noticia.fecha_scraping)}
            </div>
          </div>

          {/* Botón para ver noticia */}
          <button
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent-primary hover:bg-accent-primary/80 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Leer más
          </button>
        </div>
      </div>
    </article>
  );
}