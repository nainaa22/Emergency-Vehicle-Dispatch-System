import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import heapq

def create_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Your MySQL username
        password="tiger123",  # Your MySQL password
        database="emergency_dispatch"
    )

def fetch_vehicles(vehicle_type):
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM vehicles WHERE type = '{vehicle_type}' AND available = 1")
    vehicles = cursor.fetchall()
    conn.close()
    return vehicles

def fetch_distances():
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distances")
    distances = cursor.fetchall()
    conn.close()
    return distances

def dijkstra(source_zip, graph):
    queue, distances = [(0, source_zip)], {source_zip: 0}
    heapq.heapify(queue)

    while queue:
        current_distance, current_zip = heapq.heappop(queue)

        for neighbor, weight in graph.get(current_zip, []):
            distance = current_distance + weight
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
    return distances

def find_nearest_vehicle(vehicle_type, source_zip):
    available_vehicles = fetch_vehicles(vehicle_type)
    if not available_vehicles:
        messagebox.showinfo("Info", f"No available {vehicle_type} at the moment.")
        return None

    distance_graph = fetch_distances()
    if source_zip not in distance_graph:
        return None, None  # Invalid ZIP code

    shortest_paths = dijkstra(source_zip, distance_graph)
    nearest_vehicle = None
    min_distance = float('inf')

    for vehicle in available_vehicles:
        vehicle_zip = vehicle['location']
        if vehicle_zip in shortest_paths and shortest_paths[vehicle_zip] < min_distance:
            min_distance = shortest_paths[vehicle_zip]
            nearest_vehicle = vehicle

    return nearest_vehicle, min_distance

def dispatch_vehicle(vehicle_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE vehicles SET available = 0 WHERE id = {vehicle_id}")
    conn.commit()
    conn.close()

def dispatch_action():
    vehicle_type = vehicle_type_var.get()
    current_zip = current_zip_entry.get()

    if not current_zip.isdigit() or len(current_zip) != 5:
        result_label.config(text="Invalid ZIP code. Please enter a 5-digit ZIP code.", fg="red")
        return

    nearest_vehicle, min_distance = find_nearest_vehicle(vehicle_type, current_zip)

    if nearest_vehicle:
        vehicle_id = nearest_vehicle['id']
        response = messagebox.askyesno(
            "Dispatch",
            f"Nearest {vehicle_type} is {vehicle_id} at {min_distance} units away. Dispatch it?"
        )

        if response:
            dispatch_vehicle(vehicle_id)
            result_label.config(text=f"Vehicle {vehicle_id} dispatched successfully!", fg="green")
        else:
            result_label.config(text="Dispatch cancelled.", fg="orange")
    else:
        result_label.config(text="No available vehicle or invalid ZIP code.", fg="red")

# Tkinter UI Setup
root = tk.Tk()
root.title("Emergency Vehicle Dispatch System")

bg_color = "#f0f0f0"
title_font = ("Arial", 18, "bold")
label_font = ("Arial", 12)
entry_font = ("Arial", 12)

root.configure(bg=bg_color)

title_label = tk.Label(root, text="Emergency Vehicle Dispatch System", font=title_font, bg=bg_color)
title_label.pack(pady=10)

current_zip_label = tk.Label(root, text="Enter your current ZIP code:", font=label_font, bg=bg_color)
current_zip_label.pack(pady=5)

current_zip_entry = tk.Entry(root, font=entry_font)
current_zip_entry.pack(pady=5)

vehicle_type_label = tk.Label(root, text="Select Vehicle Type:", font=label_font, bg=bg_color)
vehicle_type_label.pack(pady=5)

vehicle_type_var = tk.StringVar(value="Ambulance")
vehicle_type_dropdown = ttk.Combobox(root, textvariable=vehicle_type_var, values=["Ambulance", "Fire Truck", "Police"], state="readonly")
vehicle_type_dropdown.pack(pady=5)

dispatch_button = tk.Button(root, text="Dispatch Vehicle", command=dispatch_action, bg="#4CAF50", fg="white", font=label_font)
dispatch_button.pack(pady=10)

result_label = tk.Label(root, text="", font=label_font, bg=bg_color)
result_label.pack(pady=5)

root.mainloop()
