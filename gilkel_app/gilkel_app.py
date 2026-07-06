import reflex as rx
from rxconfig import config
from datetime import datetime
from sqlmodel import select  

# ==========================================
# ESTRUCTURA DE LA BASE DE DATOS (TABLAS)
# ==========================================

class Usuario(rx.Model, table=True):
    # Quitamos la línea de id por completo, Reflex lo creará solo
    nombre: str
    apellido: str
    cedula: str
    telefono: str
    contrasena: str

class Proyecto(rx.Model, table=True):
    # Quitamos la línea de id por completo
    nombre: str
    participantes: str
    requerimientos: str
    fecha_inicio: str
    fecha_fin: str
    estado: str 

class Reporte(rx.Model, table=True):
    proyecto_id: int  
    observaciones: str
    fecha: str

# ==========================================
# 1. CONTROL DE ESTADO Y LÓGICA DEL SISTEMA
# ==========================================
class LoginState(rx.State):
    # =======================================================
    # MODIFICACIÓN: VARIABLES DE CONTROL PARA EL INICIO DE SESIÓN
    # =======================================================
    usuario_login_input: str = ""
    contrasena_login_input: str = ""
    
    # Tus variables de configuración originales:
    error_message: str = ""  
    cargando: bool = False   
    vista_actual: str = "proyectos"  
    usuario_autenticado: bool = False  
    usuario_conectado_nombre: str = ""
    usuario_conectado_iniciales: str = ""

    # --- VARIABLES PARA EL PANEL DE USUARIOS ---
    lista_usuarios: list[Usuario] = []

    mostrando_formulario: bool = False
    id_usuario_a_eliminar: str = ""
    alerta_eliminar_abierta: bool = False

    # Variables de texto controladas para el formulario de usuarios
    nombre_input: str = ""
    apellido_input: str = ""
    cedula_input: str = ""
    telefono_input: str = ""
    contrasena_input: str = "" 
    usuario_en_edicion_id: str = ""

    def cargar_usuarios(self):
        with rx.session() as session:
            self.lista_usuarios = session.exec(select(Usuario)).all()

    # --- VARIABLES PARA EL PANEL DE PROYECTOS ---
    lista_proyectos: list[Proyecto] = []  
    buscar_proyecto_input: str = "" 
    mostrando_form_proyecto: bool = False
    id_proyecto_a_eliminar: str = ""
    alerta_eliminar_p_abierta: bool = False
    proyecto_en_edicion_id: str = ""
    contenido_modal_ver: str = ""  

    # Variables para el modal VER requerimientos
    mostrando_modal_ver: bool = False
    requerimientos_para_ver: str = ""
    

    # Variables de control del formulario de proyectos
    nombre_proyecto_input: str = ""
    participantes_seleccionados: list[str] = []
    estatus_seleccionado: str = "" 
    fecha_inicio_input: str = ""
    fecha_fin_input: str = ""
    error_fecha_inicio: str = ""
    error_fecha_fin: str = ""
    nuevo_requerimiento_input: str = ""
    requerimientos_lista: list[str] = []


    # --- VARIABLES PARA EL PANEL DE REPORTES ---
    lista_reportes: list[dict] = []
    mostrando_form_reporte: bool = False
    id_reporte_a_eliminar: str = ""
    alerta_eliminar_r_abierta: bool = False
    reporte_en_edicion_id: str = ""

    # Variables para el modal VER observaciones de reportes
    observacion_para_ver: str = ""
    mostrando_modal_ver_r: bool = False

    # Variables de control del formulario de reportes
    proyecto_asociado_seleccionado: str = ""
    nuevo_reporte_obs_input: str = ""
    reportes_obs_lista: list[str] = []
    fecha_reporte_input: str = ""
    error_fecha_reporte: str = ""

    @rx.var
    def proyectos_con_indice(self) -> list[tuple[Proyecto, int]]:
        # Emparejamos cada proyecto con su índice dinámico en una tupla nativa
        return [(p, i) for i, p in enumerate(self.proyectos_filtrados)]
    @rx.var
    def usuarios_con_indice(self) -> list[tuple[Usuario, int]]:
        # Tomamos tu lista base de usuarios y la enumeramos para el frontend
        return [(u, i) for i, u in enumerate(self.lista_usuarios)]
    
    @rx.var
    def reportes_con_indice(self) -> list[tuple[Reporte, int]]:
        # Enumeramos cada reporte antes de mandarlo al frontend
        return [(r, i) for i, r in enumerate(self.lista_reportes)]
    
    # --- PROPIEDADES DINÁMICAS (VARS) ---
    @rx.var
    def total_proyectos(self) -> str:
        return str(len(self.lista_proyectos))
    @rx.var
    def total_en_progreso(self) -> str:
        # Cambiado p["estatus"] por p.estado
        return str(sum(1 for p in self.lista_proyectos if p.estado == "En Progreso"))

    @rx.var
    def total_pendientes(self) -> str:
        # Cambiado p["estatus"] por p.estado
        return str(sum(1 for p in self.lista_proyectos if p.estado == "Pendiente"))

    @rx.var
    def total_completados(self) -> str:
        # Cambiado p["estatus"] por p.estado
        return str(sum(1 for p in self.lista_proyectos if p.estado == "Finalizado"))

    @rx.var # o @rx.computed según como lo tengas arriba
    def opciones_usuarios(self) -> list[str]:
        # CAMBIAMOS u['nombre'] por u.nombre y u['apellido'] por u.apellido
        return [f"{u.nombre} {u.apellido}" for u in self.lista_usuarios]

    @rx.var
    def opciones_proyectos(self) -> list[str]:
        # Cambiado p["nombre"] por p.nombre
        return [p.nombre for p in self.lista_proyectos]

    @rx.var
    def proyectos_filtrados(self) -> list[Proyecto]:
        busqueda = self.buscar_proyecto_input.strip().lower()
        if not busqueda:
            return self.lista_proyectos
        # Cambiado p["nombre"] por p.nombre
        return [p for p in self.lista_proyectos if busqueda in p.nombre.lower()]

    @rx.var
    def texto_participantes_formulario(self) -> str:
        if not self.participantes_seleccionados:
            return "Seleccionar participantes..."
        if len(self.participantes_seleccionados) <= 2:
            return ", ".join(self.participantes_seleccionados)
        return f"{len(self.participantes_seleccionados)} seleccionados"

    @rx.var
    def texto_estatus_formulario(self) -> str:
        if not self.estatus_seleccionado:
            return "Seleccionar estatus inicial..."
        return self.estatus_seleccionado

    @rx.var
    def texto_proyecto_reporte_formulario(self) -> str:
        if not self.proyecto_asociado_seleccionado:
            return "Seleccionar proyecto asociado..."
        return self.proyecto_asociado_seleccionado

    @rx.var
    def titulo_formulario_usuario(self) -> str:
        return "Modificar Datos del Usuario" if self.usuario_en_edicion_id else "Completar Datos del Nuevo Usuario"

    @rx.var
    def titulo_formulario_proyecto(self) -> str:
        return "Modificar Detalles del Proyecto" if self.proyecto_en_edicion_id else "Registrar Nuevo Proyecto"

    @rx.var
    def titulo_formulario_reporte(self) -> str:
        return "Modificar Detalles del Reporte" if self.reporte_en_edicion_id else "Generar Nuevo Reporte"


    # --- EVENTOS MODAL VER (PROYECTOS Y REPORTES) ---
    @rx.event
    def abrir_modal_ver(self, requerimientos: str):
        self.contenido_modal_ver = requerimientos
        self.mostrando_modal_ver = True

    @rx.event
    def cerrar_modal_ver(self):
        self.mostrando_modal_ver = False
        self.contenido_modal_ver = ""

    @rx.event
    def abrir_modal_ver_r(self, observaciones: str):
        self.observacion_para_ver = observaciones
        self.mostrando_modal_ver_r = True

    @rx.event
    def cerrar_modal_ver_r(self):
        self.mostrando_modal_ver_r = False


    # --- EVENTOS FORMULARIO PROYECTOS ---
    @rx.event
    def cambiar_nombre_proyecto_input(self, valor: str):
        self.nombre_proyecto_input = valor

    @rx.event
    def cambiar_buscar_proyecto_input(self, valor: str):
        self.buscar_proyecto_input = valor    

    @rx.event
    def alternar_participante(self, nombre: str):
        if nombre in self.participantes_seleccionados:
            self.participantes_seleccionados.remove(nombre)
        else:
            self.participantes_seleccionados.append(nombre)

    @rx.event
    def cambiar_estatus_seleccionado(self, valor: str):
        self.estatus_seleccionado = valor

    @rx.event
    def cambiar_nuevo_requerimiento_input(self, valor: str):
        self.nuevo_requerimiento_input = valor

    @rx.event
    def añadir_requerimiento(self):
        req_limpio = self.nuevo_requerimiento_input.strip()
        if req_limpio:
            self.requerimientos_lista.append(req_limpio)
            self.nuevo_requerimiento_input = ""  

    @rx.event
    def remover_requerimiento(self, req: str):
        if req in self.requerimientos_lista:
            self.requerimientos_lista.remove(req)


    # --- EVENTOS FORMULARIO REPORTES ---
    @rx.event
    def cambiar_proyecto_asociado(self, valor: str):
        self.proyecto_asociado_seleccionado = valor

    @rx.event
    def cambiar_nuevo_reporte_obs_input(self, valor: str):
        self.nuevo_reporte_obs_input = valor

# --- EVENTOS FORMULARIO REPORTES (CORREGIDO SIN PREFIJOS) ---
    @rx.event
    def añadir_reporte_obs(self):
        obs_limpia = self.nuevo_reporte_obs_input.strip()
        if obs_limpia:
            # Guardamos exactamente lo que escribiste, sin agregar "Reporte 1:" ni nada extra
            self.reportes_obs_lista.append(obs_limpia)
            self.nuevo_reporte_obs_input = ""

    @rx.event
    def remover_reporte_obs(self, obs: str):
        if obs in self.reportes_obs_lista:
            self.reportes_obs_lista.remove(obs)
            # Ya no hace falta re-indexar con números, la lista se mantiene limpia y directa

    @rx.event
    def cambiar_usuario_login(self, valor: str):
        self.usuario_login_input = valor

    @rx.event
    def cambiar_contrasena_login(self, valor: str):
        self.contrasena_login_input = valor


    # --- VALIDACIÓN DE FECHAS ---
    def procesar_y_validar_fecha(self, valor: str) -> tuple[str, str]:
        numeros = "".join([c for c in valor if c.isdigit()])
        numeros = numeros[:8]  
        mensaje_error = ""

        if len(numeros) >= 2:
            dia = int(numeros[:2])
            if dia > 31 or dia == 0:
                mensaje_error = "Día inválido (Debe ser 01-31)"
        
        if len(numeros) >= 4:
            mes = int(numeros[2:4])
            if mes > 12 or mes == 0:
                mensaje_error = "Mes inválido (Debe ser 01-12)"

        if len(numeros) == 8:
            ano = int(numeros[4:8])
            if ano < 2026:
                mensaje_error = "El año debe ser 2026 o superior"

        if len(numeros) <= 2:
            resultado_string = numeros
        elif len(numeros) <= 4:
            resultado_string = f"{numeros[:2]}/{numeros[2:]}"
        else:
            resultado_string = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"

        return resultado_string, mensaje_error

    @rx.event
    def cambiar_fecha_inicio(self, valor: str):
        texto_formateado, error_detectado = self.procesar_y_validar_fecha(valor)
        self.fecha_inicio_input = texto_formateado
        self.error_fecha_inicio = error_detectado

    @rx.event
    def cambiar_fecha_fin(self, valor: str):
        texto_formateado, error_detectado = self.procesar_y_validar_fecha(valor)
        self.fecha_fin_input = texto_formateado
        self.error_fecha_fin = error_detectado

    @rx.event
    def cambiar_fecha_reporte(self, valor: str):
        texto_formateado, error_detectado = self.procesar_y_validar_fecha(valor)
        self.fecha_reporte_input = texto_formateado
        self.error_fecha_reporte = error_detectado


    # --- FORMATEADORES PARA USUARIOS ---
    @rx.event
    def cambiar_nombre_usuario(self, valor: str):
        self.nombre_input = valor

    @rx.event
    def cambiar_contrasena_usuario(self, valor: str):
        self.contrasena_input = valor

    @rx.event
    def cambiar_apellido_usuario(self, valor: str):
        self.apellido_input = valor

    @rx.event
    def cambiar_cedula_usuario(self, valor: str):
        numeros = "".join([c for c in valor if c.isdigit()])[:8]
        if len(numeros) <= 2:
            self.cedula_input = numeros
        elif len(numeros) <= 5:
            self.cedula_input = f"{numeros[:-3]}.{numeros[-3:]}"
        else:
            self.cedula_input = f"{numeros[:-6]}.{numeros[-6:-3]}.{numeros[-3:]}"

    @rx.event
    def cambiar_telefono_usuario(self, valor: str):
        numeros = "".join([c for c in valor if c.isdigit()])[:11]
        if len(numeros) <= 4:
            self.telefono_input = numeros
        elif len(numeros) <= 7:
            self.telefono_input = f"{numeros[:4]}-{numeros[4:]}"
        elif len(numeros) <= 9:
            self.telefono_input = f"{numeros[:4]}-{numeros[4:7]}-{numeros[7:]}"
        else:
            self.telefono_input = f"{numeros[:4]}-{numeros[4:7]}-{numeros[7:9]}-{numeros[9:]}"


    @rx.event
    def manejar_login(self, datos_formulario: dict):
        self.cargando = True
        self.error_message = ""
        
        usuario_crudo = self.usuario_login_input.strip()
        contrasena = self.contrasena_login_input.strip()

        if not usuario_crudo or not contrasena:
            self.error_message = "Por favor, llene todos los campos."
            self.cargando = False
            return

        # -----------------------------------------------------------------
        # PARO A: VALIDACIÓN DEL USUARIO RESPALDO MAESTRO
        # -----------------------------------------------------------------
        USUARIO_SEMILLA = "Adminmaxisoft" 
        CONTRASENA_SEMILLA = "max2026*"

        if usuario_crudo == USUARIO_SEMILLA and contrasena == CONTRASENA_SEMILLA:
            # PERSONALIZACIÓN PARA EL ADMIN
            self.usuario_conectado_nombre = "Administrador Maestro"
            self.usuario_conectado_iniciales = "AM"
            
            self.error_message = ""
            self.usuario_autenticado = True
            self.cargando = False
            self.vista_actual = "proyectos" 
            self.usuario_login_input = ""
            self.contrasena_login_input = ""
            return rx.redirect("/dashboard")

        # -----------------------------------------------------------------
        # PARO B: LIMPIEZA Y FORMATEO DINÁMICO DE CÉDULA
        # -----------------------------------------------------------------
        cedula_sin_puntos = usuario_crudo.replace(".", "")

        if len(cedula_sin_puntos) > 0 and cedula_sin_puntos.isdigit():
            reversed_cedula = cedula_sin_puntos[::-1]
            chunks = [reversed_cedula[i:i+3] for i in range(0, len(reversed_cedula), 3)]
            cedula_con_puntos_formateada = ".".join(chunks)[::-1]
        else:
            cedula_con_puntos_formateada = cedula_sin_puntos

        # -----------------------------------------------------------------
        # PARO C: VALIDACIÓN CONTRA POSTGRESQL + PERSONALIZACIÓN
        # -----------------------------------------------------------------
        with rx.session() as session:
            usuario_db = session.exec(
                select(Usuario).where(Usuario.cedula == cedula_con_puntos_formateada)
            ).first()

            if usuario_db and usuario_db.contrasena == contrasena:
                # PERSONALIZACIÓN PARA EL USUARIO DE BD
                self.usuario_conectado_nombre = f"{usuario_db.nombre} {usuario_db.apellido}"
                # Calculamos iniciales: Primera letra del nombre y primera del apellido
                self.usuario_conectado_iniciales = f"{usuario_db.nombre[0].upper()}{usuario_db.apellido[0].upper()}"
                
                self.error_message = ""
                self.usuario_autenticado = True  
                self.cargando = False
                self.vista_actual = "proyectos"  
                self.usuario_login_input = ""
                self.contrasena_login_input = ""
                return rx.redirect("/dashboard")
            else:
                self.error_message = "Cédula o contraseña incorrectos."
                self.cargando = False

    @rx.event
    def verificar_autenticacion(self):
        """Bloquea el acceso si el usuario no ha iniciado sesión de verdad."""
        if not self.usuario_autenticado:
            return rx.redirect("/")

    @rx.event
    def cerrar_sesion(self):
        """Limpia el estado y redirige al login."""
        self.usuario_autenticado = False
        self.error_message = ""
        self.buscar_proyecto_input = ""
        self.vista_actual = "proyectos"
        return rx.redirect("/")

    @rx.event
    def cambiar_vista(self, nueva_vista: str):
        self.vista_actual = nueva_vista

    # --- ACCIONES PANEL DE USUARIOS ---
    @rx.event
    def abrir_formulario(self):
        self.usuario_en_edicion_id = ""
        self.nombre_input = ""
        self.apellido_input = ""
        self.cedula_input = ""
        self.telefono_input = ""
        self.contrasena_input = ""  # <-- Limpiar al abrir nuevo
        self.mostrando_formulario = True

    @rx.event
    def cerrar_formulario(self):
        self.mostrando_formulario = False
        self.usuario_en_edicion_id = ""
        self.nombre_input = ""
        self.apellido_input = ""
        self.cedula_input = ""
        self.telefono_input = ""
        self.contrasena_input = ""  # <-- Limpiar al cerrar

    @rx.event
    def cargar_datos_usuario(self, id_usuario: str):
        with rx.session() as session:
            # 1. Buscamos el usuario real directamente en PostgreSQL usando su ID
            usuario = session.get(Usuario, int(id_usuario))
            
            if usuario:
                # 2. Rellenamos las variables controladas del formulario con los nombres correctos
                self.usuario_en_edicion_id = id_usuario  # Guarda el ID real de edición
                self.nombre_input = usuario.nombre
                self.apellido_input = usuario.apellido
                self.cedula_input = usuario.cedula
                self.telefono_input = usuario.telefono
                
                # Traemos la contraseña de la base de datos de manera segura por si acaso
                self.contrasena_input = getattr(usuario, "contrasena", "")
                
                # 3. Abrimos el modal/formulario de usuarios automáticamente
                self.mostrando_formulario = True

    @rx.event
    def guardar_usuario_manual(self):
        # 1. Validar usando tus variables reales (*_input) y 'self'
        if (not self.nombre_input or not self.apellido_input or 
            not self.cedula_input or not self.telefono_input):
            return rx.window_alert("Todos los campos excepto la contraseña son obligatorios.")
            
        if not self.usuario_en_edicion_id and not self.contrasena_input:
            return rx.window_alert("La contraseña es obligatoria para nuevos usuarios.")

        with rx.session() as session:
            if self.usuario_en_edicion_id:
                # MODO EDICIÓN: Buscar usando session.get con el ID correcto
                usuario = session.get(Usuario, int(self.usuario_en_edicion_id))
                if usuario:
                    usuario.nombre = self.nombre_input
                    usuario.apellido = self.apellido_input
                    usuario.cedula = self.cedula_input
                    usuario.telefono = self.telefono_input
                    # Solo actualiza la contraseña si se escribió algo en el formulario
                    if self.contrasena_input:
                        usuario.contrasena = self.contrasena_input
                    session.add(usuario)
            else:
                # MODO CREACIÓN: Guardar nuevo registro con tus variables reales
                nuevo_usuario = Usuario(
                    nombre=self.nombre_input,
                    apellido=self.apellido_input,
                    cedula=self.cedula_input,
                    telefono=self.telefono_input,
                    contrasena=self.contrasena_input
                )
                session.add(nuevo_usuario)
            
            session.commit()
        
        # Limpiar inputs correctos y cerrar modal
        self.mostrando_formulario = False
        self.usuario_en_edicion_id = ""
        self.nombre_input = ""
        self.apellido_input = ""
        self.cedula_input = ""
        self.telefono_input = ""
        self.contrasena_input = ""
        
        # Sincronizar la tabla recargando desde Postgres
        self.cargar_usuarios()

    @rx.event
    def requerir_confirmacion_eliminacion(self, user_id: str):
        self.id_usuario_a_eliminar = user_id
        self.alerta_eliminar_abierta = True

    @rx.event
    def eliminar_usuario(self, user_id: str):
        return self.requerir_confirmacion_eliminacion(user_id)

    @rx.event
    def cancelar_eliminacion(self):
        self.id_usuario_a_eliminar = ""
        self.alerta_eliminar_abierta = False

    @rx.event
    def confirmar_y_eliminar_usuario(self):
        # 1. Borramos el usuario de la base de datos real
        with rx.session() as session:
            usuario_db = session.get(Usuario, int(self.id_usuario_a_eliminar))
            if usuario_db:
                session.delete(usuario_db)
                session.commit()
        
        # 2. Cerramos la ventana de confirmación
        self.alerta_eliminar_abierta = False
        self.id_usuario_a_eliminar = ""
        
        # 3. Recargamos la lista desde la base de datos para actualizar la tabla
        self.cargar_usuarios()


    # --- ACCIONES PANEL DE PROYECTOS ---
    @rx.event
    def abrir_form_proyecto(self):
        self.proyecto_en_edicion_id = ""
        self.nombre_proyecto_input = ""
        self.participantes_seleccionados = []
        self.estatus_seleccionado = ""
        self.fecha_inicio_input = ""
        self.fecha_fin_input = ""
        self.error_fecha_inicio = ""
        self.error_fecha_fin = ""
        self.requerimientos_lista = []  
        self.nuevo_requerimiento_input = ""
        self.mostrando_form_proyecto = True
        
    @rx.event
    def cerrar_form_proyecto(self):
        self.mostrando_form_proyecto = False
        self.proyecto_en_edicion_id = ""
        self.nombre_proyecto_input = ""
        self.participantes_seleccionados = []
        self.estatus_seleccionado = ""
        self.fecha_inicio_input = ""
        self.fecha_fin_input = ""
        self.error_fecha_inicio = ""
        self.error_fecha_fin = ""
        self.requerimientos_lista = []
        self.nuevo_requerimiento_input = ""

    @rx.event
    def cargar_datos_proyecto(self, id_proyecto: str):
        with rx.session() as session:
            # 1. Buscamos el proyecto real directamente en PostgreSQL usando el ID
            proyecto = session.get(Proyecto, int(id_proyecto))
            
            if proyecto:
                # 2. Asignamos el ID para saber que estamos en Modo Edición
                self.proyecto_en_edicion_id = id_proyecto
                self.nombre_proyecto_input = proyecto.nombre
                self.estatus_seleccionado = proyecto.estado
                
                # Mapeo directo de las nuevas columnas de fechas independientes
                self.fecha_inicio_input = proyecto.fecha_inicio if proyecto.fecha_inicio else ""
                self.fecha_fin_input = proyecto.fecha_fin if proyecto.fecha_fin else ""

                # Reconstruimos la lista de requerimientos dividiendo por el salto de línea
                if proyecto.requerimientos and proyecto.requerimientos != "No especificados":
                    self.requerimientos_lista = [
                        r.strip() for r in proyecto.requerimientos.split("\n") if r.strip()
                    ]
                else:
                    self.requerimientos_lista = []

                # Reconstruimos los participantes seleccionados dividiendo por la coma
                if proyecto.participantes and proyecto.participantes != "Sin participantes":
                    self.participantes_seleccionados = [
                        p.strip() for p in proyecto.participantes.split(",") if p.strip()
                    ]
                else:
                    self.participantes_seleccionados = []

                # 3. Abrimos el formulario automáticamente con los campos llenos
                self.mostrando_form_proyecto = True

    @rx.event
    def requerir_confirmacion_proyecto(self, proy_id: str):
        self.id_proyecto_a_eliminar = proy_id
        self.alerta_eliminar_p_abierta = True

    @rx.event
    def cancelar_eliminacion_proyecto(self):
        self.id_proyecto_a_eliminar = ""
        self.alerta_eliminar_p_abierta = False

    @rx.event
    def confirmar_y_eliminar_proyecto(self):
        if not self.id_proyecto_a_eliminar:
            self.alerta_eliminar_p_abierta = False
            return

        id_proy = int(self.id_proyecto_a_eliminar)

        with rx.session() as session:
            # 1. PASO NUEVO: Buscamos y eliminamos primero todos los reportes asociados a este proyecto
            reportes_asociados = session.exec(
                select(Reporte).where(Reporte.proyecto_id == id_proy)
            ).all()
            
            for reporte in reportes_asociados:
                session.delete(reporte)

            # 2. Tu lógica original: Buscamos y borramos el proyecto real
            proyecto = session.get(Proyecto, id_proy)
            if proyecto:
                session.delete(proyecto)
                # El commit guarda AMBOS cambios de forma segura en Postgres
                session.commit()

        # 3. Cerramos el cuadro de diálogo de confirmación
        self.alerta_eliminar_p_abierta = False
        self.id_proyecto_a_eliminar = ""

        # 4. Sincronizamos las tablas recargando los datos actualizados de ambos lados
        self.cargar_reportes()  # <--- NUEVO: Recarga los reportes en el estado para limpiar la tabla visualmente
        return self.cargar_proyectos()
    
        
    @rx.event
    def guardar_proyecto_manual(self):
        nombre = self.nombre_proyecto_input.strip()
        
        if self.requerimientos_lista:
            requerimientos_unificados = "\n ".join(self.requerimientos_lista)
        else:
            requerimientos_unificados = "No especificados"
        
        inicio = self.fecha_inicio_input
        fin = self.fecha_fin_input
        participantes = ", ".join(self.participantes_seleccionados) if self.participantes_seleccionados else "Sin participantes"
        estatus = self.estatus_seleccionado if self.estatus_seleccionado else "Pendiente"

        if not nombre or not inicio or not fin:
            return rx.window_alert("Por favor, rellene los campos principales del proyecto (Nombre y Fechas).")

        if not self.requerimientos_lista:
            return rx.window_alert("Debe agregar al menos un requerimiento usando el botón (+).")

        if self.error_fecha_inicio != "" or self.error_fecha_fin != "":
            return rx.window_alert("No puede guardar el proyecto con errores en los rangos de fecha.")

        if len(inicio) < 10 or len(fin) < 10:
            return rx.window_alert("Por favor, complete ambas fechas con el formato DD/MM/AAAA.")

        try:
            fecha_inicio_objeto = datetime.strptime(inicio, "%d/%m/%Y")
            fecha_fin_objeto = datetime.strptime(fin, "%d/%m/%Y")
             
            if fecha_fin_objeto < fecha_inicio_objeto:
                return rx.window_alert("¡Error Crítico!\nLa Fecha Fin Estimada no puede ser menor a la Fecha de Inicio.")
        except ValueError:
            return rx.window_alert("Error en la estructura interna de los campos.")

        # GUARDADO EN POSTGRESQL CON NUEVAS COLUMNAS LIMPIAS
        with rx.session() as session:
            if self.proyecto_en_edicion_id:
                proyecto = session.get(Proyecto, int(self.proyecto_en_edicion_id))
                if proyecto:
                    proyecto.nombre = nombre
                    proyecto.participantes = participantes        # CORREGIDO: Guarda directo en la columna participantes
                    proyecto.requerimientos = requerimientos_unificados  # CORREGIDO: Guarda directo en la columna requerimientos
                    proyecto.fecha_inicio = inicio                # CORREGIDO: Solo la fecha de inicio
                    proyecto.fecha_fin = fin                      # CORREGIDO: Solo la fecha de fin
                    proyecto.estado = estatus
                    session.add(proyecto)
            else:
                nuevo_proyecto = Proyecto(
                    nombre=nombre,
                    participantes=participantes,                  # CORREGIDO: Campo independiente
                    requerimientos=requerimientos_unificados,      # CORREGIDO: Campo independiente
                    fecha_inicio=inicio,                          # CORREGIDO: Campo independiente
                    fecha_fin=fin,                                # CORREGIDO: Campo independiente
                    estado=estatus
                )
                session.add(nuevo_proyecto)
            
            session.commit()

        self.mostrando_form_proyecto = False
        self.proyecto_en_edicion_id = ""
        self.nombre_proyecto_input = ""
        self.participantes_seleccionados = []
        self.estatus_seleccionado = ""
        self.fecha_inicio_input = ""
        self.fecha_fin_input = ""
        self.requerimientos_lista = []
        
        # Sincroniza la tabla inmediatamente después de guardar
        return self.cargar_proyectos()
    
    
    # NUEVA FUNCIÓN: Trae los datos reales de Postgres para la tabla (Parecida a cargar_usuarios)
    @rx.event
    def cargar_proyectos(self):
        with rx.session() as session:
            resultado = session.exec(select(Proyecto).order_by(Proyecto.id)).all()
            self.lista_proyectos = resultado


    # --- ACCIONES PANEL DE REPORTES ---
    @rx.event
    def abrir_form_reporte(self):
        self.reporte_en_edicion_id = ""
        self.proyecto_asociado_seleccionado = ""
        self.nuevo_reporte_obs_input = ""
        self.reportes_obs_lista = []
        self.fecha_reporte_input = ""
        self.error_fecha_reporte = ""
        self.mostrando_form_reporte = True

    @rx.event
    def cerrar_form_reporte(self):
        self.mostrando_form_reporte = False
        self.reporte_en_edicion_id = ""
        self.proyecto_asociado_seleccionado = ""
        self.nuevo_reporte_obs_input = ""
        self.reportes_obs_lista = []
        self.fecha_reporte_input = ""
        self.error_fecha_reporte = ""

    # NUEVA FUNCIÓN: Carga todos los reportes directo de PostgreSQL
    @rx.event
    def cargar_reportes(self):
        with rx.session() as session:
            resultado = session.exec(select(Reporte).order_by(Reporte.id)).all()
            self.lista_reportes = resultado

    @rx.event
    def cargar_datos_reporte(self, rep_id: str):
        with rx.session() as session:
            reporte = session.get(Reporte, int(rep_id))
            if reporte:
                self.reporte_en_edicion_id = rep_id
                
                # Buscamos el nombre del proyecto usando su proyecto_id para rellenar tu selector visual
                proyecto = session.get(Proyecto, reporte.proyecto_id)
                if proyecto:
                    self.proyecto_asociado_seleccionado = proyecto.nombre
                else:
                    self.proyecto_asociado_seleccionado = ""

                # Validamos si no hay observaciones
                if reporte.observaciones == "Sin observaciones":
                    self.reportes_obs_lista = []
                else:
                    # Mapeamos a tu lista usando tus columnas correctas
                    self.reportes_obs_lista = reporte.observaciones.split("\n ")

                self.fecha_reporte_input = reporte.fecha
                self.error_fecha_reporte = ""
                self.mostrando_form_reporte = True

    @rx.event
    def requerir_confirmacion_reporte(self, rep_id: str):
        self.id_reporte_a_eliminar = rep_id
        self.alerta_eliminar_r_abierta = True

    @rx.event
    def cancelar_eliminacion_reporte(self):
        self.id_reporte_a_eliminar = ""
        self.alerta_eliminar_r_abierta = False

    @rx.event
    def confirmar_y_eliminar_reporte(self):
        if not self.id_reporte_a_eliminar:
            self.alerta_eliminar_r_abierta = False
            return

        with rx.session() as session:
            reporte = session.get(Reporte, int(self.id_reporte_a_eliminar))
            if reporte:
                session.delete(reporte)
                session.commit()

        self.alerta_eliminar_r_abierta = False
        self.id_reporte_a_eliminar = ""
        return self.cargar_reportes()

    @rx.event
    def guardar_reporte_manual(self):
        nombre_proyecto = self.proyecto_asociado_seleccionado.strip()
        fecha = self.fecha_reporte_input.strip()

        if self.reportes_obs_lista:
            observaciones_unificadas = "\n ".join(self.reportes_obs_lista)
        else:
            observaciones_unificadas = "Sin observaciones"

        if not nombre_proyecto or not fecha:
            return rx.window_alert("Por favor, rellene los campos obligatorios (Proyecto Asociado y Fecha del Reporte).")

        if not self.reportes_obs_lista:
            return rx.window_alert("Debe agregar al menos un reporte u observación usando el botón (+).")

        if self.error_fecha_reporte != "":
            return rx.window_alert("No puede guardar el reporte con errores en el rango de fecha.")

        if len(fecha) < 10:
            return rx.window_alert("Por favor, complete la fecha con el formato DD/MM/AAAA.")

        with rx.session() as session:
            # Buscamos de forma segura el ID real del proyecto basándonos en el nombre del menú desplegable
            proy_db = session.exec(select(Proyecto).where(Proyecto.nombre == nombre_proyecto)).first()
            id_del_proyecto = proy_db.id if proy_db else 1  # Un ID por defecto si ocurriese algo raro

            if self.reporte_en_edicion_id:
                reporte = session.get(Reporte, int(self.reporte_en_edicion_id))
                if reporte:
                    reporte.proyecto_id = id_del_proyecto
                    reporte.observaciones = observaciones_unificadas
                    reporte.fecha = fecha
                    session.add(reporte)
            else:
                nuevo_reporte = Reporte(
                    proyecto_id=id_del_proyecto,
                    observaciones=observaciones_unificadas,
                    fecha=fecha
                )
                session.add(nuevo_reporte)
            
            session.commit()

        self.mostrando_form_reporte = False
        self.reporte_en_edicion_id = ""
        self.proyecto_asociado_seleccionado = ""
        self.nuevo_reporte_obs_input = ""
        self.reportes_obs_lista = []
        self.fecha_reporte_input = ""
        
        return self.cargar_reportes()
    
# ==========================================
# 2. COMPONENTES VISUALES Y COMPLEMENTOS
# ==========================================
def obtener_badge_estatus(estatus: str) -> rx.Component:
    return rx.match(
        estatus,
        ("En Progreso", rx.badge(rx.icon(tag="play-circle", size=14), "En progreso", color_scheme="green", variant="soft", size="2")),
        ("Pendiente", rx.badge(rx.icon(tag="clock", size=14), "Pendiente", color_scheme="amber", variant="soft", size="2")),
        ("Finalizado", rx.badge(rx.icon(tag="check-circle-2", size=14), "Finalizado", color_scheme="purple", variant="soft", size="2")),
        rx.badge(estatus, color_scheme="gray")
    )

def inicio() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.image(src="/Maxisoft.png", width="420px", height="auto", margin_bottom="0.5em"),
            rx.text("Inicio de Sesión", size="5", color="#e5e7eb"),
            rx.text("¡Bienvenido!\nIngrese sus credenciales.", color="#9ca3af", size="3"),
            rx.form(
                rx.vstack(
                    rx.cond(
                        LoginState.error_message != "",
                        rx.text(LoginState.error_message, color="#ef4444", bg="rgba(239, 68, 68, 0.1)", padding="0.5em", border_radius="6px", width="100%", font_size="14px", text_align="center", border="1px solid rgba(239, 68, 68, 0.3)"),
                    ),
                    rx.vstack(
                        rx.text("Nombre de Usuario", color="#e5e7eb", font_size="14px", weight="medium"),
                        rx.input(
                            value=LoginState.usuario_login_input,
                            on_change=LoginState.cambiar_usuario_login, # <-- Enlazado limpio y directo, mano
                            placeholder="Su usuario de sistema", 
                            name="usuario_input", 
                            variant="surface", 
                            size="3", 
                            width="100%", 
                            border_radius="6px", 
                            style={"color": "#ffffff", "background-color": "rgba(30, 41, 59, 0.5)", "border-color": "#4b5563"}
                        ),
                        width="100%", align_items="start", spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", color="#e5e7eb", font_size="14px", weight="medium"),
                        rx.input(
                            value=LoginState.contrasena_login_input,
                            on_change=LoginState.cambiar_contrasena_login, # <-- Enlazado limpio y directo, mano
                            placeholder="********", 
                            type_="password", 
                            name="contrasena_input", 
                            variant="surface", 
                            size="3", 
                            width="100%", 
                            border_radius="6px", 
                            style={"color": "#ffffff", "background-color": "rgba(30, 41, 59, 0.5)", "border-color": "#4b5563"}
                        ),
                        width="100%", align_items="start", spacing="1", margin_top="0.5em",
                    ),
                    rx.hstack(rx.checkbox("Recordar mi sesión", name="recordar_check", color="#e5e7eb", size="2"), width="100%", justify="start", margin_top="0.6em"),
                    rx.button("Iniciar Sesión", type_="submit", loading=LoginState.cargando, bg="#2563eb", color="white", width="100%", margin_top="1.2em", size="3", _hover={"bg": "#1d4ed8"}),    
                    bg="rgba(17, 24, 39, 0.75)", backdrop_filter="blur(8px)", padding="2.5em 2em", border="1px solid rgba(75, 85, 99, 0.4)", box_shadow="0px 20px 25px -5px rgba(0, 0, 0, 0.5)", border_radius="12px", width="390px", spacing="3", align="center",
                ),
                on_submit=LoginState.manejar_login,  
            ),
            align="center", spacing="2", 
        ),
        min_height="100vh", width="100vw", background="radial-gradient(circle, #0f172a 0%, #1e293b 60%, #0f172a 100%)",
    )
# ==========================================
# 3. SEGUNDA PÁGINA - DASHBOARD PRINCIPAL
# ==========================================
def sidebar_item(icon: str, text: str, on_click_action=None):
    return rx.flex(
        rx.icon(tag=icon, size=20),
        rx.text(text, font_size="1em", font_weight="500"),
        spacing="3", padding="0.8em", border_radius="8px", width="100%", align="center", on_click=on_click_action,
        _hover={"bg": "rgba(255,255,255,0.1)", "cursor": "pointer", "color": "white"},
    )

def sidebar():
    return rx.vstack(
        rx.flex(
            rx.icon(tag="layout-dashboard", size=30, color="#60a5fa"),
            rx.heading("MAXISOFT", size="6", color="white"),
            spacing="3", align="center", margin_bottom="2em",
            on_click=lambda: LoginState.cambiar_vista("proyectos"), 
            _hover={"cursor": "pointer"} # Corregí 'pointer: cursor' a 'cursor: pointer'
        ),
        rx.vstack(
            sidebar_item("home", "Inicio", on_click_action=lambda: LoginState.cambiar_vista("proyectos")),
            sidebar_item("users", "Usuarios", on_click_action=lambda: LoginState.cambiar_vista("ver_usuarios")),
            sidebar_item("pie-chart", "Reportes", on_click_action=lambda: LoginState.cambiar_vista("ver_reportes")),
            spacing="1", width="100%",
        ),
        rx.spacer(),
        sidebar_item("log-out", "Cerrar Sesión", on_click_action=LoginState.cerrar_sesion), 
        
        # --- BLOQUE PERSONALIZADO CON TUS VARIABLES ---
        rx.flex(
            rx.avatar(fallback=LoginState.usuario_conectado_iniciales, size="2"),
            rx.vstack(
                rx.text(LoginState.usuario_conectado_nombre, font_size="0.8em", color="white"),
                rx.text("Usuario del sistema", font_size="0.6em", color="#94a3b8"),
                spacing="0", align_items="start",
            ),
            spacing="3", align="center", padding="1em", border_top="1px solid #334155", width="100%",
        ),
        # -----------------------------------------------
        
        background_color="#0f172a", color="#94a3b8", height="100vh", width="260px", padding="1.5em", position="fixed", left="0", top="0",
    )

def stat_card(icon: str, label: str, value: str, color_hex: str):
    return rx.vstack(
        rx.flex(
            rx.center(rx.icon(tag=icon, color=color_hex, size=24), bg=f"{color_hex}20", padding="0.5em", border_radius="10px"),
            rx.vstack(
                rx.text(value, font_size="1.4em", font_weight="bold", color="#000000"),
                rx.text(label, font_size="0.8em", color="#000000"),
                spacing="0", align_items="start",
            ),
            spacing="4", align="center",
        ),
        bg="white", padding="1.5em", border_radius="12px", box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1)", width="100%",
    )

def renderizar_fila_proyecto(proyecto_e_indice: tuple):
    # Truco definitivo de Reflex: Extraemos los datos usando el método alternativo de Var
    proyecto = proyecto_e_indice[0]
    index = proyecto_e_indice[1]
    
    # .to_string() convierte la operación reactiva a texto para el Frontend sin romper la compilación
    numero_visual = (index + 1).to_string()
    
    return rx.table.row(
        rx.table.row_header_cell(numero_visual, color="#000000"),
        rx.table.cell(proyecto.nombre, color="#000000"),
        
        # Muestra los Participantes directamente en la tabla
        rx.table.cell(proyecto.participantes, color="#000000"), 
        
        # Botón "Ver" que abre el modal mostrando SOLO los requerimientos
        rx.table.cell(
            rx.button(
                "Ver", variant="soft", color_scheme="blue", size="1",
                on_click=lambda: LoginState.abrir_modal_ver(proyecto.requerimientos),
                style={"cursor": "pointer"}
            )
        ),
        
        rx.table.cell(obtener_badge_estatus(proyecto.estado)),
        rx.table.cell(proyecto.fecha_inicio, color="#000000"),
        
        # Muestra la Fecha Fin Estimada real de la base de datos
        rx.table.cell(proyecto.fecha_fin, color="#000000"), 
        
        rx.table.cell(
            rx.hstack(
                # Mantiene el id real de Postgres para editar y borrar con seguridad
                rx.icon(tag="pencil", color="#4b5563", size=18, on_click=lambda: LoginState.cargar_datos_proyecto(proyecto.id.to_string()), style={"cursor": "pointer", "_hover": {"color": "#2563eb"}}),
                rx.icon(tag="trash-2", color="#ef4444", size=18, on_click=lambda: LoginState.requerir_confirmacion_proyecto(proyecto.id.to_string()), style={"cursor": "pointer", "_hover": {"color": "#b91c1c"}}),
                spacing="3"
            )
        )
    )

def renderizar_fila_usuario(usuario_e_indice: tuple):
    # Desempaquetamos: el objeto Usuario está en la pos 0, el índice en la pos 1
    usuario = usuario_e_indice[0]
    index = usuario_e_indice[1]
    
    # Creamos el número incremental de la fila (1, 2, 3...) seguro para el navegador
    numero_visual = (index + 1).to_string()
    
    return rx.table.row(
        # Mostramos la numeración secuencial limpia
        rx.table.row_header_cell(numero_visual, color="#000000"),
        rx.table.cell(usuario.nombre, color="#000000"),
        rx.table.cell(usuario.apellido, color="#000000"),
        rx.table.cell(usuario.cedula, color="#000000"),
        rx.table.cell(usuario.telefono, color="#000000"),
        rx.table.cell(
            rx.hstack(
                # LÁPIZ DE EDITAR: Mantiene tu lógica original con el ID real
                rx.icon(
                    tag="pencil", 
                    color="#4b5563", 
                    size=18, 
                    on_click=lambda: LoginState.cargar_datos_usuario(f"{usuario.id}"), 
                    style={"cursor": "pointer", "_hover": {"color": "#2563eb"}}
                ),
                # PAPELERA DE ELIMINAR: Mantiene tu lógica original con el ID real
                rx.icon(
                    tag="trash-2", 
                    color="#ef4444", 
                    size=18, 
                    on_click=lambda: LoginState.requerir_confirmacion_eliminacion(f"{usuario.id}"),  
                    style={"cursor": "pointer", "_hover": {"color": "#b91c1c"}}
                ),
                spacing="3"
            )
        )
    )

def renderizar_fila_reporte(reporte_e_indice: tuple):
    # Desempaquetamos la tupla: el objeto Reporte en la pos 0, el índice en la pos 1
    reporte = reporte_e_indice[0]
    index = reporte_e_indice[1]
    
    # Creamos el número incremental de la fila seguro para el navegador
    numero_visual = (index + 1).to_string()
    
    return rx.table.row(
        # Mostramos la numeración secuencial en lugar del ID de la BD
        rx.table.row_header_cell(numero_visual, color="#000000"),
        
        # Tu búsqueda mágica del nombre del proyecto se mantiene intacta usando 'reporte.proyecto_id'
        rx.table.cell(
            rx.data_list.root(
                rx.foreach(
                    LoginState.lista_proyectos,
                    lambda p: rx.cond(p.id == reporte.proyecto_id, rx.text(p.nombre), rx.fragment())
                )
            ),
            color="#000000"
        ),
        
        # Botón "Ver" funcional con las observaciones del reporte desempaquetado
        rx.table.cell(
            rx.button(
                "Ver", variant="soft", color_scheme="blue", size="1", 
                on_click=lambda: LoginState.abrir_modal_ver_r(reporte.observaciones), 
                style={"cursor": "pointer"} 
            )
        ),
        
        rx.table.cell(reporte.fecha, color="#000000"),
        
        # Acciones de Editar y Eliminar usando el ID real en string para Postgres
        rx.table.cell(
            rx.hstack(
                rx.icon(
                    tag="pencil", 
                    color="#4b5563", 
                    size=18, 
                    on_click=lambda: LoginState.cargar_datos_reporte(reporte.id.to_string()), 
                    style={"cursor": "pointer", "_hover": {"color": "#2563eb"}}
                ),
                rx.icon(
                    tag="trash-2", 
                    color="#ef4444", 
                    size=18, 
                    on_click=lambda: LoginState.requerir_confirmacion_reporte(reporte.id.to_string()), 
                    style={"cursor": "pointer", "_hover": {"color": "#b91c1c"}}
                ),
                spacing="3"
            )
        )
    )
def renderizar_fila_reporte(reporte_e_indice: tuple):
    # Desempaquetamos la tupla: el objeto Reporte en la pos 0, el índice en la pos 1
    reporte = reporte_e_indice[0]
    index = reporte_e_indice[1]
    
    # Creamos el número incremental de la fila seguro para el navegador
    numero_visual = (index + 1).to_string()
    
    return rx.table.row(
        # Mostramos la numeración secuencial en lugar del ID de la BD
        rx.table.row_header_cell(numero_visual, color="#000000"),
        
        # Tu búsqueda mágica del nombre del proyecto se mantiene intacta usando 'reporte.proyecto_id'
        rx.table.cell(
            rx.data_list.root(
                rx.foreach(
                    LoginState.lista_proyectos,
                    lambda p: rx.cond(p.id == reporte.proyecto_id, rx.text(p.nombre), rx.fragment())
                )
            ),
            color="#000000"
        ),
        
        # Botón "Ver" funcional con las observaciones del reporte desempaquetado
        rx.table.cell(
            rx.button(
                "Ver", variant="soft", color_scheme="blue", size="1", 
                on_click=lambda: LoginState.abrir_modal_ver_r(reporte.observaciones), 
                style={"cursor": "pointer"} 
            )
        ),
        
        rx.table.cell(reporte.fecha, color="#000000"),
        
        # Acciones de Editar y Eliminar usando el ID real en string para Postgres
        rx.table.cell(
            rx.hstack(
                rx.icon(
                    tag="pencil", 
                    color="#4b5563", 
                    size=18, 
                    on_click=lambda: LoginState.cargar_datos_reporte(reporte.id.to_string()), 
                    style={"cursor": "pointer", "_hover": {"color": "#2563eb"}}
                ),
                rx.icon(
                    tag="trash-2", 
                    color="#ef4444", 
                    size=18, 
                    on_click=lambda: LoginState.requerir_confirmacion_reporte(reporte.id.to_string()), 
                    style={"cursor": "pointer", "_hover": {"color": "#b91c1c"}}
                ),
                spacing="3"
            )
        )
    )

def vista_ver_usuarios():
    estilo_input_forzado = {"color": "#000000 !important", "-webkit-text-fill-color": "#000000 !important", "background-color": "#ffffff", "border-color": "#cbd5e1"}
    return rx.vstack(
        rx.flex(
            rx.vstack(rx.text("PANEL DE CONTROL:", color="#64748b", font_size="0.9em"), rx.heading("USUARIOS REGISTRADOS", size="9", font_weight="bold", color="#17159E"), align_items="start"),
            width="100%", padding_top="2em", padding_bottom="1.5em",
        ),
        rx.box(
            rx.vstack(
                rx.flex(
                    rx.icon(tag="users", color="#17159E", size=22), rx.heading("Lista de Integrantes", color="#000000", size="5"), rx.spacer(),
                    rx.button(rx.icon(tag="user-plus", size=16), "Agregar Usuario", color_scheme="blue", size="2", on_click=LoginState.abrir_formulario),
                    spacing="4", align="center", padding_bottom="1.5em", border_bottom="1px solid #e2e8f0", width="100%",
                ),
                # ENVOLTURA PARA EL SCROLL CONGELADO (Mantiene la tabla estable)
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("#", color="#000000", font_weight="bold"),
                                rx.table.column_header_cell("Nombre", color="#000000", font_weight="bold"),
                                rx.table.column_header_cell("Apellido", color="#000000", font_weight="bold"),
                                rx.table.column_header_cell("Cédula", color="#000000", font_weight="bold"),
                                rx.table.column_header_cell("Número de Teléfono", color="#000000", font_weight="bold"),
                                rx.table.column_header_cell("Acciones", color="#000000", font_weight="bold"),
                            )
                        ),
                        # UN SOLO rx.table.body usando la nueva lista computada con índices
                        rx.table.body(
                            rx.foreach(
                                LoginState.usuarios_con_indice, 
                                renderizar_fila_usuario
                            )
                        ),
                        width="100%", variant="surface", margin_top="1.5em",
                    ),
                    max_height="380px",
                    overflow_y="auto",
                    width="100%",
                ),
                width="100%",
            ),
            bg="white", padding="2.5em", border_radius="16px", box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)", width="100%",
        ),
        
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.flex(
                        rx.icon(tag="user-plus", color="#17159E", size=22), 
                        rx.heading(LoginState.titulo_formulario_usuario, color="#000000", size="4"), 
                        spacing="2", align="center"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.grid(
                                rx.vstack(
                                    rx.text("Nombre", font_weight="600", color="#000000", font_size="14px"),
                                    rx.input(placeholder="Nombre", value=LoginState.nombre_input, on_change=LoginState.cambiar_nombre_usuario, style=estilo_input_forzado, width="100%")
                                ),
                                rx.vstack(
                                    rx.text("Apellido", font_weight="600", color="#000000", font_size="14px"),
                                    rx.input(placeholder="Apellido", value=LoginState.apellido_input, on_change=LoginState.cambiar_apellido_usuario, style=estilo_input_forzado, width="100%")
                                ),
                                rx.vstack(
                                    rx.text("Cédula", font_weight="600", color="#000000", font_size="14px"),
                                    rx.input(placeholder="Ej: 30.364.777", value=LoginState.cedula_input, on_change=LoginState.cambiar_cedula_usuario, max_length=10, style=estilo_input_forzado, width="100%")
                                ),
                                rx.vstack(
                                    rx.text("Teléfono", font_weight="600", color="#000000", font_size="14px"),
                                    rx.input(placeholder="Ej: 0412-123-45-67", value=LoginState.telefono_input, on_change=LoginState.cambiar_telefono_usuario, max_length=14, style=estilo_input_forzado, width="100%")
                                ),
                                # -------------------------------------------------------------
                                # NUEVO CAMPO CONTRASEÑA (Visible solo en Formulario/Edición)
                                # -------------------------------------------------------------
                                rx.vstack(
                                    rx.text("Contraseña", font_weight="600", color="#000000", font_size="14px"),
                                    rx.input(
                                        placeholder="Contraseña de acceso", 
                                        value=LoginState.contrasena_input, 
                                        on_change=LoginState.cambiar_contrasena_usuario, 
                                        style=estilo_input_forzado, 
                                        width="100%"
                                    )
                                ),
                                columns="2", spacing="4", width="100%", margin_top="1em"
                            ),
                            rx.flex(
                                rx.button("Cancelar", variant="surface", color_scheme="red", on_click=LoginState.cerrar_formulario, type_="button", style={"cursor": "pointer"}),
                                rx.button("Guardar Usuario", color_scheme="blue", type_="button", on_click=LoginState.guardar_usuario_manual, style={"cursor": "pointer"}),
                                spacing="3", width="100%", justify="end", margin_top="1.5em"
                            ),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "550px"}
            ),
            open=LoginState.mostrando_formulario,
        ),

        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.flex(rx.icon(tag="alert-triangle", color="#ef4444", size=24), rx.heading("¿Deseas eliminar este usuario?", color="#000000", size="4"), spacing="2", align="center"),
                    rx.text("Esta acción no se puede deshacer. El integrante será removido de la lista permanentemente.", color="#4b5563", font_size="14px", margin_top="0.5em"),
                    rx.flex(
                        rx.button("No, Cancelar", variant="surface", color_scheme="gray", on_click=LoginState.cancelar_eliminacion, type_="button", style={"cursor": "pointer"}),
                        rx.button("Sí, Eliminar", color_scheme="red", on_click=LoginState.confirmar_y_eliminar_usuario, type_="button", style={"cursor": "pointer"}),
                        spacing="3", width="100%", justify="end", margin_top="1.5em"
                    ),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "450px"}
            ),
            open=LoginState.alerta_eliminar_abierta,
        ),
        max_width="1200px", width="100%",
    )

def vista_proyectos_principal():
    style_input_forzado = {
        "color": "#000000 !important", 
        "-webkit-text-fill-color": "#000000 !important", 
        "background-color": "#ffffff !important", 
        "border-color": "#cbd5e1",
        "opacity": "1 !important"
    }
    
    return rx.vstack(
        rx.flex(
            rx.vstack(rx.text("BIENVENIDO AL SISTEMA DE:", color="#64748b"), rx.heading("GESTIÓN DE PROYECTOS", size="8", font_weight="bold", color="#17159E"), align_items="start"),
            rx.spacer(), rx.icon(tag="bell", size=24, color="#64748b"), 
            width="100%", align="center", padding_y="2em",
        ),
        
        rx.grid(
            stat_card("folder", "Proyectos", LoginState.total_proyectos, "#3b82f6"), 
            stat_card("play-circle", "En progreso", LoginState.total_en_progreso, "#10b981"), 
            stat_card("clock", "Pendientes", LoginState.total_pendientes, "#f59e0b"), 
            stat_card("check-circle-2", "Completados", LoginState.total_completados, "#8b5cf6"), 
            columns="4", spacing="4", width="100%"
        ),
        
        rx.box(
            rx.vstack(
                rx.flex(
                    rx.heading("Proyectos Recientes", color="#000000", size="5"), 
                    rx.spacer(), 
                    rx.hstack(
                        rx.input(
                            placeholder="Buscar proyecto por nombre...",
                            size="3",
                            width="320px",
                            variant="surface",
                            style=style_input_forzado,
                            value=LoginState.buscar_proyecto_input,
                            on_change=LoginState.cambiar_buscar_proyecto_input,
                        ), 
                        rx.button(rx.icon(tag="plus", size=16), "Agregar Proyecto", color_scheme="blue", on_click=LoginState.abrir_form_proyecto),
                        spacing="3", align_items="center"
                    ),
                    width="100%", align_items="center", padding_bottom="1.5em"
                ), 
                
                # --- AQUÍ EMPIEZA EL TRUCO DEL PISO MÁXIMO Y LA BARRA VERTICAL ---
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID", color="#000000"),
                                rx.table.column_header_cell("Nombre del Proyecto", color="#000000"),
                                rx.table.column_header_cell("Participantes", color="#000000"), 
                                rx.table.column_header_cell("Requerimientos", color="#000000"),
                                rx.table.column_header_cell("Estatus", color="#000000"),
                                rx.table.column_header_cell("F. Inicio", color="#000000"),
                                rx.table.column_header_cell("F. Fin Estimada", color="#000000"),
                                rx.table.column_header_cell("Acciones", color="#000000"),
                            ),
                        ),
                        # LIMPIO: Un solo body para que actúe como hijo directo de table.root
                        rx.table.body(
                            rx.foreach(
                                LoginState.proyectos_con_indice, 
                                renderizar_fila_proyecto
                            )
                        ),
                        width="100%",
                        variant="surface",
                    ),
                    max_height="380px",    # Pone el piso para congelar el crecimiento hacia abajo
                    overflow_y="auto",     # Activa la barra vertical automática a la derecha si es necesario
                    width="100%",
                    style={
                        "scrollbar-width": "thin",  # Barra más delgada en navegadores compatibles (Firefox)
                        "&::-webkit-scrollbar": {"width": "6px"},  # Ancho de la barra en Chrome/Edge
                        "&::-webkit-scrollbar-thumb": {"background-color": "#cbd5e1", "border-radius": "4px"} # Gris suave
                    }
                ),
                # --- AQUÍ TERMINA EL CONTENEDOR CON SCROLL ---
            ), 
            bg="white", padding="2em", border_radius="16px", box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)", margin_top="2em", width="100%"
        ),

        # Formulario de Proyecto
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.flex(
                        rx.icon(tag="folder-plus", color="#17159E", size=22), 
                        rx.heading(LoginState.titulo_formulario_proyecto, color="#000000", size="4"), 
                        spacing="2", align="center"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.grid(
                                rx.vstack(
                                    rx.text("Nombre del Proyecto", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.input(
                                        placeholder="Ej. Sistema de Inventario", 
                                        value=LoginState.nombre_proyecto_input,
                                        on_change=LoginState.cambiar_nombre_proyecto_input,
                                        style=style_input_forzado, 
                                        width="100%"
                                    )
                                ),
                                
                                rx.vstack(
                                    rx.text("Participantes", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.menu.root(
                                        rx.menu.trigger(
                                            rx.button(
                                                rx.flex(
                                                    rx.text(LoginState.texto_participantes_formulario, font_weight="normal", color="#4b5563"),
                                                    rx.spacer(),
                                                    rx.icon(tag="chevron-down", size=16, color="#4b5563"),
                                                    align="center", width="100%"
                                                ),
                                                variant="outline", width="100%", style={"background-color": "#ffffff", "border-color": "#cbd5e1", "padding-x": "0.8em"}
                                            )
                                        ),
                                        rx.menu.content(
                                            rx.foreach(
                                                LoginState.opciones_usuarios,
                                                lambda usuario: rx.menu.item(
                                                    rx.hstack(
                                                        rx.checkbox(
                                                            checked=LoginState.participantes_seleccionados.contains(usuario),
                                                            on_change=lambda _: LoginState.alternar_participante(usuario)
                                                        ),
                                                        rx.text(usuario, color="#000000"),
                                                        spacing="2"
                                                    ),
                                                    close_on_select=False
                                                )
                                            ),
                                            style={"background-color": "#ffffff", "border": "1px solid #cbd5e1"}
                                        )
                                    ),
                                    width="100%"
                                ),

                                rx.vstack(
                                    rx.text("Requerimientos del Proyecto", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.hstack(
                                        rx.input(
                                            placeholder="Ej. Servidor local, Python 3.12", 
                                            value=LoginState.nuevo_requerimiento_input,
                                            on_change=LoginState.cambiar_nuevo_requerimiento_input,
                                            style=style_input_forzado, 
                                            width="82%"
                                        ),
                                        rx.button(
                                            rx.icon(tag="plus", size=16), 
                                            type_="button",
                                            color_scheme="blue",
                                            on_click=lambda: LoginState.añadir_requerimiento(),
                                            style={"cursor": "pointer"}
                                        ),
                                        width="100%"
                                    ),
                                    rx.flex(
                                        rx.foreach(
                                            LoginState.requerimientos_lista,
                                            lambda req: rx.badge(
                                                req,
                                                rx.icon(
                                                    tag="x", 
                                                    size=12, 
                                                    style={"cursor": "pointer", "margin_left": "5px"},
                                                    on_click=lambda: LoginState.remover_requerimiento(req)
                                                ),
                                                color_scheme="blue", variant="surface", margin="2px"
                                            )
                                        ),
                                        wrap="wrap", width="100%", padding_top="4px"
                                    ),
                                    width="100%"
                                ),
                                
                                rx.vstack(
                                    rx.text("Estatus Inicial", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.menu.root(
                                        rx.menu.trigger(
                                            rx.button(
                                                rx.flex(
                                                    rx.text(LoginState.texto_estatus_formulario, font_weight="normal", color="#4b5563"),
                                                    rx.spacer(),
                                                    rx.icon(tag="chevron-down", size=16, color="#4b5563"),
                                                    align="center", width="100%"
                                                ),
                                                variant="outline", 
                                                width="100%", 
                                                style={"background-color": "#ffffff", "border-color": "#cbd5e1", "padding-x": "0.8em", "cursor": "pointer"}
                                            )
                                        ),
                                        rx.menu.content(
                                            rx.menu.item("Pendiente", on_click=lambda: LoginState.cambiar_estatus_seleccionado("Pendiente"), style={"color": "#000000"}),
                                            rx.menu.item("En Progreso", on_click=lambda: LoginState.cambiar_estatus_seleccionado("En Progreso"), style={"color": "#000000"}),
                                            rx.menu.item("Finalizado", on_click=lambda: LoginState.cambiar_estatus_seleccionado("Finalizado"), style={"color": "#000000"}),
                                            style={"background-color": "#ffffff", "border": "1px solid #cbd5e1"}
                                        )
                                    ),
                                    width="100%"
                                ),

                                rx.vstack(
                                    rx.text("Fecha Inicio", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.input(
                                        placeholder="DD/MM/AAAA", 
                                        value=LoginState.fecha_inicio_input,
                                        on_change=LoginState.cambiar_fecha_inicio,
                                        max_length=10, 
                                        style=style_input_forzado, 
                                        width="100%"
                                    ),
                                    rx.cond(
                                        LoginState.error_fecha_inicio != "",
                                        rx.text(LoginState.error_fecha_inicio, color="#ef4444", font_size="12px", font_weight="semibold", margin_top="2px")
                                    ),
                                    width="100%", align_items="start"
                                ),

                                rx.vstack(
                                    rx.text("Fecha Fin Estimada", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.input(
                                        placeholder="DD/MM/AAAA", 
                                        value=LoginState.fecha_fin_input,
                                        on_change=LoginState.cambiar_fecha_fin,
                                        max_length=10, 
                                        style=style_input_forzado, 
                                        width="100%"
                                    ),
                                    rx.cond(
                                        LoginState.error_fecha_fin != "",
                                        rx.text(LoginState.error_fecha_fin, color="#ef4444", font_size="12px", font_weight="semibold", margin_top="2px")
                                    ),
                                    width="100%", align_items="start"
                                ),

                                columns="2", spacing="4", width="100%", margin_top="1em"
                            ),
                            
                            rx.flex(
                                rx.button("Cancelar", variant="surface", color_scheme="red", on_click=LoginState.cerrar_form_proyecto, type_="button", style={"cursor": "pointer"}),
                                rx.button("Guardar Proyecto", color_scheme="blue", type_="button", on_click=LoginState.guardar_proyecto_manual, style={"cursor": "pointer"}),
                                spacing="3", width="100%", justify="end", margin_top="1.5em"
                            ),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "550px"}
            ),
            open=LoginState.mostrando_form_proyecto,
        ),

        # Alerta de Confirmación de Eliminación
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.flex(rx.icon(tag="alert-triangle", color="#ef4444", size=24), rx.heading("¿Deseas eliminar este proyecto?", color="#000000", size="4"), spacing="2", align="center"),
                    rx.text("Esta acción borrará el proyecto permanentemente de los registros.", color="#4b5563", font_size="14px", margin_top="0.5em"),
                    rx.flex(
                        rx.button("No, Cancelar", variant="surface", color_scheme="gray", on_click=LoginState.cancelar_eliminacion_proyecto, type_="button", style={"cursor": "pointer"}),
                        rx.button("Sí, Eliminar", color_scheme="red", on_click=LoginState.confirmar_y_eliminar_proyecto, type_="button", style={"cursor": "pointer"}),
                        spacing="3", width="100%", justify="end", margin_top="1.5em"
                    ),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "450px"}
            ),
            open=LoginState.alerta_eliminar_p_abierta,
        ),
       
        # Modales de Requerimientos
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Requerimientos del Proyecto", color="#000000"),
                rx.dialog.description(
                    rx.text(LoginState.contenido_modal_ver, white_space="pre-line", color="#374151"),
                    margin_top="1em"
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cerrar",
                            variant="solid",
                            color_scheme="blue",
                            on_click=LoginState.cerrar_modal_ver,
                            type_="button",
                            style={
                                "cursor": "pointer",
                                "background-color": "#437fda",
                                "color": "#ffffff",
                                "padding": "0.5em 2em",
                                "border-radius": "6px"
                            }
                        )
                    ),
                    justify="end",
                    margin_top="2em"
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "500px"}
            ),
            open=LoginState.mostrando_modal_ver,
        ),

        max_width="1200px", width="100%", margin="0 auto",
    )

def vista_reportes_principal():
    estilo_input_forzado = {
        "color": "#000000 !important", 
        "-webkit-text-fill-color": "#000000 !important", 
        "background-color": "#ffffff !important", 
        "border-color": "#cbd5e1",
        "opacity": "1 !important"
    }

    return rx.vstack(
        rx.flex(
            rx.vstack(rx.text("PANEL DE SEGUIMIENTO:", color="#64748b"), rx.heading("REPORTES Y OBSERVACIONES", size="8", font_weight="bold", color="#17159E"), align_items="start"),
            width="100%", padding_top="2em", padding_bottom="1.5em",
        ),

        # CUADRO PRINCIPAL DE REPORTES 
        rx.box(
            rx.vstack(
                rx.flex(
                    rx.heading("Historial de Reportes", color="#000000", size="5"), 
                    rx.spacer(), 
                    rx.hstack(
                        rx.input(placeholder="Buscar reportes...", width="220px"), 
                        rx.button(rx.icon(tag="file-text", size=16), "Generar Reporte", color_scheme="blue", on_click=LoginState.abrir_form_reporte),
                        spacing="3", align_items="center"
                    ),
                    width="100%", align_items="center", padding_bottom="1.5em"
                ), 

                # Contenedor interno con scroll vertical para la tabla
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("# (ID)", color="#000000", font_weight="bold"), 
                                rx.table.column_header_cell("Nombre del Proyecto", color="#000000", font_weight="bold"), 
                                rx.table.column_header_cell("Reporte / Observación", color="#000000", font_weight="bold"), 
                                rx.table.column_header_cell("Fecha del Reporte", color="#000000", font_weight="bold"),  
                                rx.table.column_header_cell("Acciones", color="#000000", font_weight="bold") 
                            )
                        ), 
                        # UN SOLO rx.table.body usando el protocolo unificado de tuplas indexadas
                        rx.table.body(
                            rx.foreach(
                                LoginState.reportes_con_indice, 
                                renderizar_fila_reporte
                            )
                        ),
                        width="100%", variant="surface"
                    ),
                    max_height="480px",  # Altura máxima antes de activar la barra
                    overflow_y="auto",   # Activa la barra de desplazamiento vertical solo si es necesario
                    width="100%",
                )
            ),
            bg="white", padding="2em", border_radius="16px", box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)", width="100%"
        ),

        # DIÁLOGO FORMULARIO DE REPORTES
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.flex(
                        rx.icon(tag="file-plus", color="#17159E", size=22), 
                        rx.heading(LoginState.titulo_formulario_reporte, color="#000000", size="4"), 
                        spacing="2", align="center"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.grid(
                                # Dropdown de Proyectos Creados
                                rx.vstack(
                                    rx.text("Proyecto Asociado", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.menu.root(
                                        rx.menu.trigger(
                                            rx.button(
                                                rx.flex(
                                                    rx.text(LoginState.texto_proyecto_reporte_formulario, font_weight="normal", color="#4b5563"),
                                                    rx.spacer(),
                                                    rx.icon(tag="chevron-down", size=16, color="#4b5563"),
                                                    align="center", width="100%"
                                                ),
                                                variant="outline", width="100%", style={"background-color": "#ffffff", "border-color": "#cbd5e1", "padding-x": "0.8em", "cursor": "pointer"}
                                            )
                                        ),
                                        rx.menu.content(
                                            rx.cond(
                                                LoginState.opciones_proyectos.length() == 0,
                                                rx.menu.item("No hay proyectos creados", disabled=True, style={"color": "#94a3b8"}),
                                                rx.foreach(
                                                    LoginState.opciones_proyectos,
                                                    lambda proy: rx.menu.item(proy, on_click=lambda: LoginState.cambiar_proyecto_asociado(proy), style={"color": "#000000"})
                                                )
                                            ),
                                            style={"background-color": "#ffffff", "border": "1px solid #cbd5e1"}
                                        )
                                    ),
                                    width="100%"
                                ),

                                # Fecha del Reporte
                                rx.vstack(
                                    rx.text("Fecha del Reporte", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.input(
                                        placeholder="DD/MM/AAAA", 
                                        value=LoginState.fecha_reporte_input,
                                        on_change=LoginState.cambiar_fecha_reporte,
                                        max_length=10, 
                                        style=estilo_input_forzado, 
                                        width="100%"
                                    ),
                                    rx.cond(
                                        LoginState.error_fecha_reporte != "",
                                        rx.text(LoginState.error_fecha_reporte, color="#ef4444", font_size="12px", font_weight="semibold", margin_top="2px")
                                    ),
                                    width="100%", align_items="start"
                                ),

                                # Carga de observaciones dinámicas con botón (+)
                                rx.vstack(
                                    rx.text("Reportes y Observaciones", font_weight="600", color="#000000", font_size="14px"), 
                                    rx.hstack(
                                        rx.input(
                                            placeholder="Añadir observación del avance...", 
                                            value=LoginState.nuevo_reporte_obs_input,
                                            on_change=LoginState.cambiar_nuevo_reporte_obs_input,
                                            style=estilo_input_forzado, 
                                            width="82%"
                                        ),
                                        rx.button(
                                            rx.icon(tag="plus", size=16), 
                                            type_="button",
                                            color_scheme="blue",
                                            on_click=lambda: LoginState.añadir_reporte_obs(),
                                            style={"cursor": "pointer"}
                                        ),
                                        width="100%"
                                    ),
                                    rx.flex(
                                        rx.foreach(
                                            LoginState.reportes_obs_lista,
                                            lambda obs: rx.badge(
                                                obs,
                                                rx.icon(
                                                    tag="x", 
                                                    size=12, 
                                                    style={"cursor": "pointer", "margin_left": "5px"},
                                                    on_click=lambda: LoginState.remover_reporte_obs(obs)
                                                ),
                                                color_scheme="blue", variant="surface", margin="2px"
                                            )
                                        ),
                                        wrap="wrap", width="100%", padding_top="4px"
                                    ),
                                    width="100%"
                                ),

                                columns="1", spacing="4", width="100%", margin_top="1em"
                            ),

                            rx.flex(
                                rx.button("Cancelar", variant="surface", color_scheme="red", on_click=LoginState.cerrar_form_reporte, type_="button", style={"cursor": "pointer"}),
                                rx.button("Guardar Reporte", color_scheme="blue", type_="button", on_click=LoginState.guardar_reporte_manual, style={"cursor": "pointer"}),
                                spacing="3", width="100%", justify="end", margin_top="1.5em"
                            ),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "550px"}
            ),
            open=LoginState.mostrando_form_reporte,
        ),

        # ELIMINACIÓN DE REPORTES
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.flex(rx.icon(tag="alert-triangle", color="#ef4444", size=24), rx.heading("¿Deseas eliminar este reporte?", color="#000000", size="4"), spacing="2", align="center"),
                    rx.text("Esta acción borrará el reporte permanentemente de los registros.", color="#4b5563", font_size="14px", margin_top="0.5em"),
                    rx.flex(
                        rx.button("No, Cancelar", variant="surface", color_scheme="gray", on_click=LoginState.cancelar_eliminacion_reporte, type_="button", style={"cursor": "pointer"}),
                        rx.button("Sí, Eliminar", color_scheme="red", on_click=LoginState.confirmar_y_eliminar_reporte, type_="button", style={"cursor": "pointer"}),
                        spacing="3", width="100%", justify="end", margin_top="1.5em"
                    ),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "450px"}
            ),
            open=LoginState.alerta_eliminar_r_abierta,
        ),

        # DIÁLOGO VER OBSERVACIONES COMPLETA
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.heading("Observaciones Registradas", color="#000000", size="4"),
                    rx.text(LoginState.observacion_para_ver, color="#4b5563", font_size="14px", margin_top="0.5em", style={"white-space": "pre-wrap"}),
                    rx.button("Cerrar", variant="surface", color_scheme="gray", on_click=LoginState.cerrar_modal_ver_r, type_="button", style={"cursor": "pointer"}),
                    width="100%",
                ),
                style={"background-color": "#ffffff", "border-radius": "12px", "padding": "2em", "max_width": "450px"}
            ),
            open=LoginState.mostrando_modal_ver_r,
        ),
        max_width="1200px", width="100%", margin="0 auto",
    )

def dashboard_page():
    return rx.flex(
        sidebar(), 
        rx.box(
            rx.match(
                LoginState.vista_actual,
                ("proyectos", vista_proyectos_principal()),
                ("ver_usuarios", vista_ver_usuarios()),
                ("ver_reportes", vista_reportes_principal()),
                rx.text("Página no encontrada")
            ),
            flex="1", margin_left="260px", padding_x="4em", background_color="#f1f5f9", min_height="100vh",
        ),
        width="100%",
        # AGREGA ESTO AQUÍ para sincronizar con Postgres al cargar el componente
        on_mount=[LoginState.cargar_usuarios, LoginState.cargar_proyectos, LoginState.cargar_reportes]
    )

app = rx.App(
    theme=rx.theme(
        has_background=True, 
        accent_color="blue", 
        radius="large",      
    )
)
app.add_page(inicio, route="/")
# Se ejecuta 'verificar_autenticacion' cada vez que la página intente cargar
app.add_page(dashboard_page, route="/dashboard", on_load=LoginState.verificar_autenticacion)