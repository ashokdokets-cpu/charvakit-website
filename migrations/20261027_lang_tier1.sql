-- Language Tier 1 extension: JavaScript, Java, TypeScript
-- Idempotent — safe to re-run.

-- 1. Add language column to assessments (may not exist)
ALTER TABLE charvak_career_assessments
  ADD COLUMN IF NOT EXISTS language text;

-- 2. JavaScript/Node.js task classes (12)
INSERT INTO charvak_cert_task_classes
  (class_id, format, language, class_key, class_label, description)
VALUES
  ('TC-C-JS-ARRAYS','coding','javascript','arrays','Arrays & Objects','Array and object manipulation, destructuring'),
  ('TC-C-JS-ASYNC','coding','javascript','async','Async & Promises','Promises, async/await, event loop'),
  ('TC-C-JS-CLOSURES','coding','javascript','closures','Closures & Scope','Lexical scope, hoisting, IIFE'),
  ('TC-C-JS-PROTOTYPES','coding','javascript','prototypes','Prototypes & Classes','Prototype chain, class syntax'),
  ('TC-C-JS-ERRORS','coding','javascript','errors','Error Handling','try/catch, custom errors'),
  ('TC-C-JS-JSON','coding','javascript','json','JSON & Serialization','JSON.parse, JSON.stringify, edge cases'),
  ('TC-C-JS-STRINGS','coding','javascript','strings','String Manipulation','Template literals, methods'),
  ('TC-C-JS-FP','coding','javascript','functional','Functional Patterns','map/filter/reduce, immutability'),
  ('TC-C-JS-NODE','coding','javascript','node_modules','Node.js Modules','require, exports, ESM imports'),
  ('TC-C-JS-NUMBERS','coding','javascript','numbers','Numbers & BigInt','Floating point, BigInt edge cases'),
  ('TC-C-JS-EDGE','coding','javascript','edge_cases','Edge Case Handling','Falsy values, undefined vs null'),
  ('TC-C-JS-QUALITY','coding','javascript','code_quality','Code Quality','Readability, DRY, idiomatic JS')
ON CONFLICT (class_id) DO NOTHING;

-- 3. Java 17 task classes (11)
INSERT INTO charvak_cert_task_classes
  (class_id, format, language, class_key, class_label, description)
VALUES
  ('TC-C-JAVA-COLLECTIONS','coding','java','collections','Collections Framework','List, Map, Set, iterators'),
  ('TC-C-JAVA-OOP','coding','java','oop','OOP Design','Inheritance, polymorphism, interfaces'),
  ('TC-C-JAVA-EXCEPTIONS','coding','java','exceptions','Exceptions','try/catch, custom exceptions'),
  ('TC-C-JAVA-GENERICS','coding','java','generics','Generics','Type parameters, bounds, wildcards'),
  ('TC-C-JAVA-STREAMS','coding','java','streams','Streams & Lambdas','Functional operations on collections'),
  ('TC-C-JAVA-CONCURRENCY','coding','java','concurrency','Concurrency','Threads, executors, synchronized'),
  ('TC-C-JAVA-STRINGS','coding','java','strings','String Manipulation','StringBuilder, format, methods'),
  ('TC-C-JAVA-IO','coding','java','io','I/O & Files','File operations, streams'),
  ('TC-C-JAVA-MEMORY','coding','java','memory','Memory & GC','Object lifecycle, references'),
  ('TC-C-JAVA-EDGE','coding','java','edge_cases','Edge Cases','Null, empty, overflow handling'),
  ('TC-C-JAVA-QUALITY','coding','java','code_quality','Code Quality','Naming, structure, idiom usage')
ON CONFLICT (class_id) DO NOTHING;

-- 4. TypeScript task classes (11)
INSERT INTO charvak_cert_task_classes
  (class_id, format, language, class_key, class_label, description)
VALUES
  ('TC-C-TS-TYPES','coding','typescript','type_system','Type System','Interfaces, unions, enums'),
  ('TC-C-TS-GENERICS','coding','typescript','generics','Generics & Constraints','Type parameters, extends, keyof'),
  ('TC-C-TS-NARROWING','coding','typescript','narrowing','Type Guards & Narrowing','typeof, instanceof, custom guards'),
  ('TC-C-TS-ASYNC','coding','typescript','async','Async Patterns','Promises, async/await, typed results'),
  ('TC-C-TS-UTILITY','coding','typescript','utility_types','Utility Types','Partial, Pick, Omit, Record'),
  ('TC-C-TS-INTEROP','coding','typescript','interop','JS Interop','any, unknown, declare'),
  ('TC-C-TS-MODULES','coding','typescript','modules','Module Resolution','import/export, namespaces'),
  ('TC-C-TS-ERRORS','coding','typescript','errors','Error Handling','Typed error handling'),
  ('TC-C-TS-EDGE','coding','typescript','edge_cases','Edge Cases','Null/undefined, strict mode'),
  ('TC-C-TS-PERF','coding','typescript','performance','Performance','Type-level vs runtime cost'),
  ('TC-C-TS-QUALITY','coding','typescript','code_quality','Code Quality','Readability, type clarity')
ON CONFLICT (class_id) DO NOTHING;