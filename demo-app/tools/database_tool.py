"""
Langflow Custom Component: Database Tool
Queries PostgreSQL database using dynamic credentials from Vault
"""

from typing import Any
import psycopg2
import json

from lfx.custom import Component
from lfx.io import MessageTextInput, StrInput, DataInput, Output
from lfx.schema import Data


class DatabaseToolComponent(Component):
    display_name = "Database Tool"
    description = "STEP 2: Query the employee database using credentials from get_credentials. CRITICAL: You must FIRST call get_credentials, then pass its RESULT object (containing username/password) as the vault_credentials parameter. DO NOT pass a function reference - pass the actual credentials data returned by get_credentials."
    documentation = "https://www.postgresql.org/docs/"
    icon = "Database"
    name = "database_tool"
    
    inputs = [
        DataInput(
            name="vault_credentials",
            display_name="Vault Credentials",
            info="Dynamic database credentials from Vault Tool",
            tool_mode=True,
        ),
        MessageTextInput(
            name="query_type",
            display_name="Query Type",
            info="Type of query: 'basic_info' for employee basic information or 'salary_info' for salary data",
            tool_mode=True,
        ),
        StrInput(
            name="employee_id",
            display_name="Employee ID",
            info="Optional: Specific employee ID to query (leave empty for all employees)",
            value="",
            tool_mode=True,
        ),
        StrInput(
            name="db_host",
            display_name="Database Host",
            info="PostgreSQL database host",
            value="localhost",
            advanced=True,
        ),
        StrInput(
            name="db_port",
            display_name="Database Port",
            info="PostgreSQL database port",
            value="5432",
            advanced=True,
        ),
        StrInput(
            name="db_name",
            display_name="Database Name",
            info="PostgreSQL database name",
            value="employee_db",
            advanced=True,
        ),
    ]
    
    outputs = [
        Output(
            display_name="Query Results",
            name="results",
            method="query_database",
        ),
    ]
    
    def query_database(self) -> Data:
        """
        Query the database using dynamic credentials
        
        Returns:
            Data object with query results or error information
        """
        try:
            # Extract credentials from Vault Tool output
            creds = self.vault_credentials
            
            # Handle different input formats
            if hasattr(creds, 'data'):
                creds_data = creds.data
            elif isinstance(creds, str):
                # Parse JSON string if credentials come as string
                try:
                    creds_data = json.loads(creds)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON in vault_credentials: {str(e)}"
                    self.log(error_msg)
                    self.status = "❌ Invalid credentials format"
                    return Data(
                        data={
                            "error": error_msg,
                            "status": "failed"
                        }
                    )
            else:
                creds_data = creds
            
            # Check if credentials retrieval was successful
            if creds_data.get("status") == "failed":
                error_msg = f"Cannot query database: {creds_data.get('error', 'Unknown error')}"
                self.log(error_msg)
                self.status = "❌ Invalid credentials"
                return Data(
                    data={
                        "error": error_msg,
                        "status": "failed"
                    }
                )
            
            username = creds_data.get("username")
            password = creds_data.get("password")
            
            if not username or not password:
                error_msg = "Missing username or password in credentials"
                self.log(error_msg)
                self.status = "❌ Invalid credentials"
                return Data(
                    data={
                        "error": error_msg,
                        "status": "failed"
                    }
                )
            
            # Extract query type
            query_type = self.query_type
            if hasattr(query_type, 'text'):
                query_type = query_type.text.lower()
            else:
                query_type = str(query_type).lower()
            
            # Determine which table to query and build SQL
            if "basic" in query_type or "basic_info" in query_type:
                table_name = "employee_basic_info"
                if self.employee_id and self.employee_id.strip():
                    sql_query = (
                        "SELECT employee_id, first_name, last_name, email, department, "
                        "job_title, hire_date, office_location "
                        "FROM employee_basic_info WHERE employee_id = %s"
                    )
                    query_params = (self.employee_id.strip(),)
                    self.log(f"Querying employee_basic_info for employee_id: {self.employee_id}")
                else:
                    sql_query = (
                        "SELECT employee_id, first_name, last_name, email, department, "
                        "job_title, hire_date, office_location "
                        "FROM employee_basic_info ORDER BY employee_id LIMIT 10"
                    )
                    query_params = None
                    self.log("Querying employee_basic_info for all employees (limit 10)")
            elif "salary" in query_type or "salary_info" in query_type:
                table_name = "employee_salary_info"
                # JOIN with basic_info to include employee name alongside salary data
                if self.employee_id and self.employee_id.strip():
                    sql_query = (
                        "SELECT b.employee_id, b.first_name, b.last_name, b.department, "
                        "s.annual_salary, s.bonus_percentage, s.stock_options, "
                        "s.salary_grade, s.performance_rating "
                        "FROM employee_salary_info s "
                        "JOIN employee_basic_info b ON s.employee_id = b.employee_id "
                        "WHERE s.employee_id = %s"
                    )
                    query_params = (self.employee_id.strip(),)
                    self.log(f"Querying salary info for employee_id: {self.employee_id}")
                else:
                    sql_query = (
                        "SELECT b.employee_id, b.first_name, b.last_name, b.department, "
                        "s.annual_salary, s.bonus_percentage, s.stock_options, "
                        "s.salary_grade, s.performance_rating "
                        "FROM employee_salary_info s "
                        "JOIN employee_basic_info b ON s.employee_id = b.employee_id "
                        "ORDER BY s.employee_id LIMIT 10"
                    )
                    query_params = None
                    self.log("Querying salary info for all employees (limit 10)")
            else:
                error_msg = f"Invalid query type: {query_type}. Use 'basic_info' or 'salary_info'"
                self.log(error_msg)
                self.status = "❌ Invalid query type"
                return Data(
                    data={
                        "error": error_msg,
                        "status": "failed"
                    }
                )
            
            # Connect to database
            self.log(f"Connecting to database as user: {username}")
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=username,
                password=password,
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            # Execute query
            if query_params:
                cursor.execute(sql_query, query_params)
            else:
                cursor.execute(sql_query)
            
            # Fetch results
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(column_names, row)))
            
            # Close connection
            cursor.close()
            conn.close()
            
            # Return results
            result_data = {
                "status": "success",
                "table": table_name,
                "row_count": len(results),
                "data": results
            }
            
            self.log(f"✓ Successfully queried {table_name}: {len(results)} rows returned")
            self.status = f"✓ Query successful: {len(results)} rows"
            
            return Data(data=result_data)
            
        except psycopg2.Error as e:
            error_msg = f"Database error: {str(e)}"
            self.log(error_msg)
            
            # Check if it's a permission error
            if "permission denied" in str(e).lower():
                self.status = "❌ Permission denied"
                error_msg = f"Access denied: User does not have permission to access {table_name}"
            else:
                self.status = "❌ Database error"
            
            return Data(
                data={
                    "error": error_msg,
                    "status": "failed"
                }
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log(error_msg)
            self.status = "❌ Unexpected error"
            return Data(
                data={
                    "error": error_msg,
                    "status": "failed"
                }
            )

# Made with Bob
