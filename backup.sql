-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: evaluacion_ia
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alumnos`
--

DROP TABLE IF EXISTS `alumnos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumnos` (
  `id_alumno` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_alumno`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alumnos`
--

LOCK TABLES `alumnos` WRITE;
/*!40000 ALTER TABLE `alumnos` DISABLE KEYS */;
INSERT INTO `alumnos` VALUES (1,'Carlos Ramirez','carlos@gmail.com'),(2,'Laura Torres','laura@gmail.com'),(3,'Andres Lopez','andres02@gmail.com'),(4,'Sofia Martinez','sofia@gmail.com'),(5,'Daniela Rojas','daniela@gmail.com'),(6,'Luis Fernandez','luis@gmail.com'),(7,'Camila Vargas','camila@gmail.com'),(8,'Miguel Castro','miguelcastro00@gmail.com'),(9,'Valentina Ruiz','valentina@gmail.com'),(10,'Sebastian Herrera','sebastian@gmail.com'),(11,'Ingrid Torres','ingrid123@gmail.com');
/*!40000 ALTER TABLE `alumnos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluacion`
--

DROP TABLE IF EXISTS `evaluacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluacion` (
  `id_evaluacion` int NOT NULL AUTO_INCREMENT,
  `id_alumno` int DEFAULT NULL,
  `puntaje` decimal(5,2) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `id_modulo` int DEFAULT NULL,
  `id_examen` int DEFAULT NULL,
  `nombre_examen` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_evaluacion`),
  KEY `id_alumno` (`id_alumno`),
  KEY `id_modulo` (`id_modulo`),
  CONSTRAINT `evaluacion_ibfk_1` FOREIGN KEY (`id_alumno`) REFERENCES `alumnos` (`id_alumno`),
  CONSTRAINT `evaluacion_ibfk_2` FOREIGN KEY (`id_modulo`) REFERENCES `modulos` (`id_modulo`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluacion`
--

LOCK TABLES `evaluacion` WRITE;
/*!40000 ALTER TABLE `evaluacion` DISABLE KEYS */;
INSERT INTO `evaluacion` VALUES (1,1,4.50,'2026-04-12',1,1,NULL),(2,2,3.80,'2026-04-12',1,1,NULL),(3,3,5.00,'2026-04-13',1,1,NULL),(4,4,2.50,'2026-04-13',1,1,NULL),(5,5,4.20,'2026-04-14',1,1,NULL),(6,6,3.00,'2026-04-14',2,3,NULL),(7,7,4.80,'2026-04-14',2,3,NULL),(8,8,3.70,'2026-04-14',2,3,NULL),(9,9,2.90,'2026-04-14',3,4,NULL),(10,10,4.10,'2026-04-14',3,4,NULL),(11,1,4.50,'2026-04-15',NULL,NULL,NULL),(12,11,2.50,'2026-04-16',NULL,NULL,NULL);
/*!40000 ALTER TABLE `evaluacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `examenes`
--

DROP TABLE IF EXISTS `examenes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `examenes` (
  `id_examen` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `id_modulo` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `total_preguntas` int DEFAULT NULL,
  PRIMARY KEY (`id_examen`),
  KEY `id_modulo` (`id_modulo`),
  CONSTRAINT `examenes_ibfk_1` FOREIGN KEY (`id_modulo`) REFERENCES `modulos` (`id_modulo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `examenes`
--

LOCK TABLES `examenes` WRITE;
/*!40000 ALTER TABLE `examenes` DISABLE KEYS */;
INSERT INTO `examenes` VALUES (1,'Examen lgebra',1,'2026-04-10',10),(2,'Examen Geometra',1,'2026-04-15',10),(3,'Examen Literatura',2,'2026-04-12',10),(4,'Examen Biologa',3,'2026-04-14',10),(5,'Examen Algebra',1,'2026-04-01',10);
/*!40000 ALTER TABLE `examenes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modulos`
--

DROP TABLE IF EXISTS `modulos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modulos` (
  `id_modulo` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `color` varchar(20) DEFAULT '#667eea',
  PRIMARY KEY (`id_modulo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modulos`
--

LOCK TABLES `modulos` WRITE;
/*!40000 ALTER TABLE `modulos` DISABLE KEYS */;
INSERT INTO `modulos` VALUES (1,'Matemticas','lgebra, geometra y clculo','#48bb78'),(2,'Lengua Espaola','Gramtica, literatura y redaccin','#4299e1'),(3,'Ciencias Naturales','Biologa, qumica y fsica','#ed8936'),(4,'Historia','Historia universal y nacional','#9f7aea'),(5,'Ingls','Vocabulario y gramtica inglesa','#f56565');
/*!40000 ALTER TABLE `modulos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pregunta`
--

DROP TABLE IF EXISTS `pregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pregunta` (
  `id_pregunta` int NOT NULL AUTO_INCREMENT,
  `descripcion` text,
  `respuesta_correcta` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_pregunta`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pregunta`
--

LOCK TABLES `pregunta` WRITE;
/*!40000 ALTER TABLE `pregunta` DISABLE KEYS */;
INSERT INTO `pregunta` VALUES (1,'2 + 2 = ?','4'),(2,'5 x 3 = ?','15'),(3,'10 - 6 = ?','4'),(4,'Capital de Colombia','Bogota'),(5,'Color del cielo en un dia despejado','Azul'),(6,'3 + 7 = ?','10'),(7,'9 x 2 = ?','18'),(8,'15 / 3 = ?','5'),(9,'Raiz cuadrada de 16','4'),(10,'Cuantos dias tiene una semana','7');
/*!40000 ALTER TABLE `pregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `respuesta`
--

DROP TABLE IF EXISTS `respuesta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `respuesta` (
  `id_respuesta` int NOT NULL AUTO_INCREMENT,
  `id_evaluacion` int DEFAULT NULL,
  `id_pregunta` int DEFAULT NULL,
  `es_correcta` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_respuesta`),
  KEY `id_evaluacion` (`id_evaluacion`),
  KEY `id_pregunta` (`id_pregunta`),
  CONSTRAINT `respuesta_ibfk_1` FOREIGN KEY (`id_evaluacion`) REFERENCES `evaluacion` (`id_evaluacion`),
  CONSTRAINT `respuesta_ibfk_2` FOREIGN KEY (`id_pregunta`) REFERENCES `pregunta` (`id_pregunta`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `respuesta`
--

LOCK TABLES `respuesta` WRITE;
/*!40000 ALTER TABLE `respuesta` DISABLE KEYS */;
INSERT INTO `respuesta` VALUES (1,1,1,1),(2,1,2,1),(3,1,3,0),(4,1,4,1),(5,1,5,1),(6,1,6,1),(7,1,7,0),(8,1,8,1),(9,1,9,1),(10,1,10,1),(11,2,1,1),(12,2,2,0),(13,2,3,1),(14,2,4,1),(15,2,5,0),(16,2,6,1),(17,2,7,1),(18,2,8,0),(19,2,9,1),(20,2,10,1),(21,3,1,1),(22,3,2,1),(23,3,3,1),(24,3,4,1),(25,3,5,1),(26,3,6,1),(27,3,7,1),(28,3,8,1),(29,3,9,1),(30,3,10,1),(31,11,1,1),(32,11,2,1),(33,12,1,0),(34,12,2,0),(35,12,3,0),(36,12,4,0),(37,12,5,0),(38,12,6,0),(39,12,7,0),(40,12,8,0),(41,12,9,0),(42,12,10,0);
/*!40000 ALTER TABLE `respuesta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-16 15:06:57
