import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from psycopg2.extras import RealDictCursor

from app.db import get_db_connection


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "autocare-development-key")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    # =========================
    # КЛИЕНТИ
    # =========================

    @app.route("/customers")
    def customers():
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM customers
                    ORDER BY id DESC
                """)
                customers_list = cur.fetchall()

        return render_template("customers.html", customers=customers_list)

    @app.route("/customers/add", methods=["POST"])
    def add_customer():
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not first_name or not last_name or not email:
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("customers"))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO customers
                        (first_name, last_name, email, phone)
                        VALUES (%s, %s, %s, %s)
                    """, (first_name, last_name, email, phone))

            flash("Клиентът е добавен успешно!", "success")
        except Exception:
            flash("Грешка: този имейл може вече да съществува.", "error")

        return redirect(url_for("customers"))

    @app.route("/customers/edit/<int:customer_id>", methods=["POST"])
    def edit_customer(customer_id):
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not first_name or not last_name or not email:
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("customers"))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE customers
                        SET first_name = %s,
                            last_name = %s,
                            email = %s,
                            phone = %s
                        WHERE id = %s
                    """, (first_name, last_name, email, phone, customer_id))

            flash("Данните са обновени успешно!", "success")
        except Exception:
            flash("Грешка при редактирането. Провери имейла.", "error")

        return redirect(url_for("customers"))

   
    @app.route("/customers/delete/<int:customer_id>", methods=["POST"])
    def delete_customer(customer_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Проверка за свързани автомобили
                    cur.execute(
                        "SELECT COUNT(*) FROM vehicles WHERE customer_id = %s",
                        (customer_id,)
                    )
                    vehicle_count = cur.fetchone()[0]

                    if vehicle_count > 0:
                        flash(
                            "Клиентът не може да бъде изтрит: има "
                            "свързани автомобили.",
                            "error"
                        )
                        return redirect(url_for("customers"))

                    # Изтриване, ако няма свързани автомобили
                    cur.execute(
                        "DELETE FROM customers WHERE id = %s",
                        (customer_id,)
                    )

                    if cur.rowcount == 0:
                        flash("Клиентът не беше намерен.", "error")
                    else:
                        flash("Клиентът е изтрит успешно!", "success")

        except Exception:
            flash(
                "Възникна грешка при изтриването на клиента.",
                "error"
            )

        return redirect(url_for("customers"))

    # =========================
    # АВТОМОБИЛИ
    # =========================

    @app.route("/vehicles")
    def vehicles():
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        v.id,
                        v.customer_id,
                        v.brand,
                        v.model,
                        v.registration_number,
                        v.year,
                        c.first_name,
                        c.last_name
                    FROM vehicles v
                    JOIN customers c ON c.id = v.customer_id
                    ORDER BY v.id DESC
                """)
                vehicles_list = cur.fetchall()

                cur.execute("""
                    SELECT id, first_name, last_name
                    FROM customers
                    ORDER BY first_name, last_name
                """)
                customers_list = cur.fetchall()

        return render_template(
            "vehicles.html",
            vehicles=vehicles_list,
            customers=customers_list
        )

    @app.route("/vehicles/add", methods=["POST"])
    def add_vehicle():
        customer_id = request.form.get("customer_id", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        registration_number = request.form.get(
            "registration_number", ""
        ).strip().upper()
        year = request.form.get("year", "").strip()

        if not all([customer_id, brand, model, registration_number, year]):
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("vehicles"))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO vehicles
                        (customer_id, brand, model, registration_number, year)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (customer_id, brand, model, registration_number, year))

            flash("Автомобилът е добавен успешно!", "success")
        except Exception:
            flash(
                "Грешка при добавянето. Провери клиента и регистрационния номер.",
                "error"
            )

        return redirect(url_for("vehicles"))

    @app.route("/vehicles/edit/<int:vehicle_id>", methods=["POST"])
    def edit_vehicle(vehicle_id):
        customer_id = request.form.get("customer_id", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        registration_number = request.form.get(
            "registration_number", ""
        ).strip().upper()
        year = request.form.get("year", "").strip()

        if not all([customer_id, brand, model, registration_number, year]):
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("vehicles"))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE vehicles
                        SET customer_id = %s,
                            brand = %s,
                            model = %s,
                            registration_number = %s,
                            year = %s
                        WHERE id = %s
                    """, (
                        customer_id,
                        brand,
                        model,
                        registration_number,
                        year,
                        vehicle_id
                    ))

            flash("Автомобилът е обновен успешно!", "success")
        except Exception:
            flash(
                "Грешка при редактирането. Провери данните и регистрационния номер.",
                "error"
            )

        return redirect(url_for("vehicles"))

    @app.route("/vehicles/delete/<int:vehicle_id>", methods=["POST"])
    def delete_vehicle(vehicle_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM vehicles WHERE id = %s",
                        (vehicle_id,)
                    )

            flash("Автомобилът е изтрит успешно!", "success")
        except Exception:
            flash(
                "Автомобилът не може да бъде изтрит, защото има свързани записи.",
                "error"
            )

        return redirect(url_for("vehicles"))

    # =========================
    # СЕРВИЗНИ УСЛУГИ
    # =========================

    @app.route("/services")
    def services():
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM services
                    ORDER BY id DESC
                """)
                services_list = cur.fetchall()

        return render_template(
            "services.html",
            services=services_list
        )

    @app.route("/services/add", methods=["POST"])
    def add_service():
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()
        duration = request.form.get("duration_minutes", "").strip()

        if not name or not price or not duration:
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("services"))

        try:
            price_value = float(price)
            duration_value = int(duration)

            if price_value < 0 or duration_value <= 0:
                raise ValueError

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO services
                        (name, description, price, duration_minutes)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        name,
                        description,
                        price_value,
                        duration_value
                    ))

            flash("Услугата е добавена успешно!", "success")

        except ValueError:
            flash("Въведи валидна цена и продължителност.", "error")
        except Exception:
            flash("Грешка при добавянето на услугата.", "error")

        return redirect(url_for("services"))

    @app.route("/services/edit/<int:service_id>", methods=["POST"])
    def edit_service(service_id):
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()
        duration = request.form.get("duration_minutes", "").strip()

        if not name or not price or not duration:
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("services"))

        try:
            price_value = float(price)
            duration_value = int(duration)

            if price_value < 0 or duration_value <= 0:
                raise ValueError

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE services
                        SET name = %s,
                            description = %s,
                            price = %s,
                            duration_minutes = %s
                        WHERE id = %s
                    """, (
                        name,
                        description,
                        price_value,
                        duration_value,
                        service_id
                    ))

            flash("Услугата е обновена успешно!", "success")

        except ValueError:
            flash("Въведи валидна цена и продължителност.", "error")
        except Exception:
            flash("Грешка при редактирането на услугата.", "error")

        return redirect(url_for("services"))

    @app.route("/services/delete/<int:service_id>", methods=["POST"])
    def delete_service(service_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM services WHERE id = %s",
                        (service_id,)
                    )

            flash("Услугата е изтрита успешно!", "success")

        except Exception:
            flash(
                "Услугата не може да бъде изтрита, защото има свързани записи.",
                "error"
            )

        return redirect(url_for("services"))

   
    # =========================
    # ЗАПИСВАНЕ НА ЧАСОВЕ
    # =========================

    @app.route("/appointments")
    def appointments():
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        a.id,
                        a.vehicle_id,
                        a.service_id,
                        a.appointment_date,
                        a.status,
                        a.notes,
                        v.brand,
                        v.model,
                        v.registration_number,
                        c.first_name,
                        c.last_name,
                        s.name AS service_name
                    FROM appointments a
                    JOIN vehicles v ON v.id = a.vehicle_id
                    JOIN customers c ON c.id = v.customer_id
                    JOIN services s ON s.id = a.service_id
                    ORDER BY a.appointment_date DESC
                """)
                appointments_list = cur.fetchall()

                cur.execute("""
                    SELECT
                        v.id,
                        v.brand,
                        v.model,
                        v.registration_number,
                        c.first_name,
                        c.last_name
                    FROM vehicles v
                    JOIN customers c ON c.id = v.customer_id
                    ORDER BY v.registration_number
                """)
                vehicles_list = cur.fetchall()

                cur.execute("""
                    SELECT id, name, price
                    FROM services
                    ORDER BY name
                """)
                services_list = cur.fetchall()

        return render_template(
            "appointments.html",
            appointments=appointments_list,
            vehicles=vehicles_list,
            services=services_list
        )

    @app.route("/appointments/add", methods=["POST"])
    def add_appointment():
        vehicle_id = request.form.get("vehicle_id", "").strip()
        service_id = request.form.get("service_id", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        status = request.form.get("status", "scheduled").strip()
        notes = request.form.get("notes", "").strip()

        if not all([vehicle_id, service_id, appointment_date, appointment_time]):
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("appointments"))

        if status not in ["scheduled", "completed", "cancelled"]:
            flash("Невалиден статус на часа.", "error")
            return redirect(url_for("appointments"))

        try:
            appointment_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}",
                "%d.%m.%Y %H:%M"
            )

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO appointments
                        (vehicle_id, service_id, appointment_date, status, notes)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        vehicle_id,
                        service_id,
                        appointment_datetime,
                        status,
                        notes
                    ))

            flash("Часът е записан успешно!", "success")

        except ValueError:
            flash("Въведи валидна дата и час.", "error")
        except Exception:
            flash("Грешка при записването на часа. Провери автомобила и услугата.", "error")

        return redirect(url_for("appointments"))

    @app.route("/appointments/edit/<int:appointment_id>", methods=["POST"])
    def edit_appointment(appointment_id):
        vehicle_id = request.form.get("vehicle_id", "").strip()
        service_id = request.form.get("service_id", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        status = request.form.get("status", "").strip()
        notes = request.form.get("notes", "").strip()

        if not all([vehicle_id, service_id, appointment_date, appointment_time]):
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("appointments"))

        if status not in ["scheduled", "completed", "cancelled"]:
            flash("Невалиден статус на часа.", "error")
            return redirect(url_for("appointments"))

        try:
            appointment_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}",
                "%d.%m.%Y %H:%M"
            )

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE appointments
                        SET vehicle_id = %s,
                            service_id = %s,
                            appointment_date = %s,
                            status = %s,
                            notes = %s
                        WHERE id = %s
                    """, (
                        vehicle_id,
                        service_id,
                        appointment_datetime,
                        status,
                        notes,
                        appointment_id
                    ))

            flash("Часът е обновен успешно!", "success")

        except ValueError:
            flash("Въведи валидна дата и час.", "error")
        except Exception:
            flash("Грешка при редактирането на часа.", "error")

        return redirect(url_for("appointments"))

    @app.route("/appointments/delete/<int:appointment_id>", methods=["POST"])
    def delete_appointment(appointment_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM appointments
                        WHERE id = %s
                        AND NOT EXISTS (
                            SELECT 1 FROM repairs
                            WHERE repairs.appointment_id = appointments.id
                        )
                    """, (appointment_id,))

                    deleted = cur.rowcount

            if deleted:
                flash("Часът е изтрит успешно!", "success")
            else:
                flash(
                    "Часът не може да бъде изтрит, защото има свързан ремонт.",
                    "error"
                )

        except Exception:
            flash("Грешка при изтриването на часа.", "error")

        return redirect(url_for("appointments"))

       # =========================
    # УПРАВЛЕНИЕ НА РЕМОНТИ
    # =========================

    @app.route("/repairs")
    def repairs():
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        r.id,
                        r.appointment_id,
                        r.description,
                        r.cost,
                        r.status,
                        r.start_date,
                        r.end_date,
                        v.brand,
                        v.model,
                        v.registration_number,
                        c.first_name,
                        c.last_name,
                        s.name AS service_name
                    FROM repairs r
                    JOIN appointments a ON a.id = r.appointment_id
                    JOIN vehicles v ON v.id = a.vehicle_id
                    JOIN customers c ON c.id = v.customer_id
                    JOIN services s ON s.id = a.service_id
                    ORDER BY r.start_date DESC
                """)
                repairs_list = cur.fetchall()

                cur.execute("""
                    SELECT
                        a.id,
                        a.appointment_date,
                        v.brand,
                        v.model,
                        v.registration_number,
                        c.first_name,
                        c.last_name,
                        s.name AS service_name
                    FROM appointments a
                    JOIN vehicles v ON v.id = a.vehicle_id
                    JOIN customers c ON c.id = v.customer_id
                    JOIN services s ON s.id = a.service_id
                    ORDER BY a.appointment_date DESC
                """)
                appointments_list = cur.fetchall()

        return render_template(
            "repairs.html",
            repairs=repairs_list,
            appointments=appointments_list
        )

    @app.route("/repairs/add", methods=["POST"])
    def add_repair():
        appointment_id = request.form.get("appointment_id", "").strip()
        description = request.form.get("description", "").strip()
        cost = request.form.get("cost", "0").strip()
        status = request.form.get("status", "in_progress").strip()

        if not all([appointment_id, description, cost]):
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("repairs"))

        if status not in ["in_progress", "completed"]:
            flash("Невалиден статус на ремонта.", "error")
            return redirect(url_for("repairs"))

        try:
            repair_cost = float(cost)

            if repair_cost < 0:
                raise ValueError

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO repairs
                        (appointment_id, description, cost, status, end_date)
                        VALUES (%s, %s, %s, %s,
                                CASE WHEN %s = 'completed'
                                THEN CURRENT_TIMESTAMP ELSE NULL END)
                    """, (
                        appointment_id,
                        description,
                        repair_cost,
                        status,
                        status
                    ))

            flash("Ремонтът е добавен успешно!", "success")

        except ValueError:
            flash("Въведи валидна неотрицателна цена.", "error")
        except Exception:
            flash("Грешка при добавянето на ремонта.", "error")

        return redirect(url_for("repairs"))

    @app.route("/repairs/edit/<int:repair_id>", methods=["POST"])
    def edit_repair(repair_id):
        description = request.form.get("description", "").strip()
        cost = request.form.get("cost", "").strip()
        status = request.form.get("status", "").strip()

        if not all([description, cost]):
            flash("Попълни всички задължителни полета.", "error")
            return redirect(url_for("repairs"))

        if status not in ["in_progress", "completed"]:
            flash("Невалиден статус на ремонта.", "error")
            return redirect(url_for("repairs"))

        try:
            repair_cost = float(cost)

            if repair_cost < 0:
                raise ValueError

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE repairs
                        SET description = %s,
                            cost = %s,
                            status = %s,
                            end_date = CASE
                                WHEN %s = 'completed'
                                THEN COALESCE(end_date, CURRENT_TIMESTAMP)
                                ELSE NULL
                            END
                        WHERE id = %s
                    """, (
                        description,
                        repair_cost,
                        status,
                        status,
                        repair_id
                    ))

            flash("Ремонтът е обновен успешно!", "success")

        except ValueError:
            flash("Въведи валидна неотрицателна цена.", "error")
        except Exception:
            flash("Грешка при редактирането на ремонта.", "error")

        return redirect(url_for("repairs"))

    @app.route("/repairs/delete/<int:repair_id>", methods=["POST"])
    def delete_repair(repair_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM repairs WHERE id = %s",
                        (repair_id,)
                    )

            flash("Ремонтът е изтрит успешно!", "success")

        except Exception:
            flash("Грешка при изтриването на ремонта.", "error")

        return redirect(url_for("repairs"))
   
   
    return app
