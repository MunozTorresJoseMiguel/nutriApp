-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 26-11-2025 a las 04:49:10
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `usuarios_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellidos` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `edad` tinyint(3) UNSIGNED DEFAULT NULL,
  `genero` enum('masculino','femenino','otro') DEFAULT NULL,
  `altura_cm` smallint(5) UNSIGNED DEFAULT NULL,
  `peso_kg` decimal(5,2) DEFAULT NULL,
  `actividad` varchar(50) DEFAULT NULL,
  `objetivo` varchar(50) DEFAULT NULL,
  `goal_other` varchar(255) DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `apellidos`, `email`, `password`, `edad`, `genero`, `altura_cm`, `peso_kg`, `actividad`, `objetivo`, `goal_other`, `fecha_registro`) VALUES
(3, 'Jose Miguel', '', 'jose@gmail.com', 'scrypt:32768:8:1$M36YVl7TQfcsL439$b7b8e729ad37028e6dbd039e7230bf65643d91dc73e612b333be620807870564eb4288170053b1038b68665fb625f65729883648ffd94a26c976ada33d75d7a9', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-11-26 02:21:58'),
(4, 'Angel Joaquin', 'Muñoz Torres', 'angelmunoz@gmail.com', 'scrypt:32768:8:1$oYvDW3BH9lqfX1im$64caea0af4bb1393fd48a790b1c7a64b87f268b0a28b0514126a9a35ab2f5487cea52bdc4f735a839bc2a910ec766ee5d90199af5e01edc596a3b6d83061853f', 20, 'masculino', 179, 140.00, 'ligero', 'perder_peso', NULL, '2025-11-26 03:15:39');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_goals`
--

CREATE TABLE `usuario_goals` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `goal` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indices de la tabla `usuario_goals`
--
ALTER TABLE `usuario_goals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `usuario_goals`
--
ALTER TABLE `usuario_goals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `usuario_goals`
--
ALTER TABLE `usuario_goals`
  ADD CONSTRAINT `usuario_goals_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
