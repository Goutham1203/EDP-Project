from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import bcrypt
from datetime import datetime
from database import db
from blockchain import Blockchain

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'

# --- HELPER FUNCTIONS ---
def get_system_state():
    state = db.execute_fetchone("SELECT start_time, end_time FROM system_state WHERE id = 1")
    now = datetime.now()
    active = False
    
    if state and state['start_time'] and state['end_time']:
        active = state['start_time'] <= now <= state['end_time']
        
    return {
        'active': active,
        'start_time': state['start_time'] if state else None,
        'end_time': state['end_time'] if state else None
    }

def login_required(role=None):
    def wrapper(fn):
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("Unauthorized access", "error")
                return redirect(url_for('index'))
            return fn(*args, **kwargs)
        decorated_view.__name__ = fn.__name__
        return decorated_view
    return wrapper

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        user = db.execute_fetchone("SELECT * FROM users WHERE username = %s", (username,))
        
        if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['has_voted'] = user['has_voted']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('voter_dashboard'))
        else:
            flash("Invalid credentials", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        # Check if username exists
        existing_user = db.execute_fetchone("SELECT id FROM users WHERE username = %s", (username,))
        if existing_user:
            flash("Username already taken", "error")
            return render_template('register.html')

        role = request.form.get('role', 'voter')
        # Ensure role is either admin or voter to prevent injection
        if role not in ['admin', 'voter']:
            role = 'voter'
            
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        db.execute_query("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", (username, hashed, role), commit=True)
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- VOTER ROUTES ---

@app.route('/voter_dashboard')
@login_required(role='voter')
def voter_dashboard():
    # Update has_voted from DB to be sure
    user = db.execute_fetchone("SELECT has_voted FROM users WHERE id = %s", (session['user_id'],))
    session['has_voted'] = user['has_voted']
    
    candidates = db.execute_query("SELECT * FROM candidates")
    state = get_system_state()
    return render_template('voter_dashboard.html', candidates=candidates, has_voted=session['has_voted'], state=state)

@app.route('/cast_vote', methods=['POST'])
@login_required(role='voter')
def cast_vote():
    state = get_system_state()
    if not state['active']:
        flash("Voting is currently inactive.", "error")
        return redirect(url_for('voter_dashboard'))

    # Double check if user already voted
    user = db.execute_fetchone("SELECT has_voted FROM users WHERE id = %s", (session['user_id'],))
    if user['has_voted']:
        flash("You have already voted.", "error")
        return redirect(url_for('voter_dashboard'))

    candidate_id = request.form['candidate_id']
    voter_id = session['user_id']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get the latest block (vote) to get previous_hash
    last_vote = db.execute_fetchone("SELECT hash FROM votes ORDER BY id DESC LIMIT 1")
    previous_hash = last_vote['hash'] if last_vote else "0000000000000000000000000000000000000000000000000000000000000000"

    # Calculate new hash
    new_hash = Blockchain.calculate_hash(voter_id, candidate_id, timestamp, previous_hash)

    # Insert vote into blockchain
    db.execute_query(
        "INSERT INTO votes (voter_id, candidate_id, timestamp, previous_hash, hash) VALUES (%s, %s, %s, %s, %s)",
        (voter_id, candidate_id, timestamp, previous_hash, new_hash),
        commit=True
    )

    # Update user has_voted status
    db.execute_query("UPDATE users SET has_voted = TRUE WHERE id = %s", (voter_id,), commit=True)
    session['has_voted'] = True

    flash("Your vote has been cast successfully!", "success")
    return redirect(url_for('voter_dashboard'))


# --- ADMIN ROUTES ---

@app.route('/admin_dashboard')
@login_required(role='admin')
def admin_dashboard():
    return redirect(url_for('admin_schedule'))

@app.route('/admin/schedule')
@login_required(role='admin')
def admin_schedule():
    candidates = db.execute_query("SELECT * FROM candidates")
    state = get_system_state()
    return render_template('admin_schedule.html', candidates=candidates, state=state)

@app.route('/admin/monitoring')
@login_required(role='admin')
def admin_monitoring():
    state = get_system_state()
    
    # Calculate results
    votes = db.execute_query("SELECT * FROM votes ORDER BY id ASC")
    is_valid, msg = Blockchain.verify_chain(votes)
    
    tally = db.execute_query("""
        SELECT c.name, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
    """)
    
    return render_template('admin_monitoring.html', state=state, valid=is_valid, msg=msg, results=tally)

@app.route('/admin/voters')
@login_required(role='admin')
def admin_voters():
    voters = db.execute_query("SELECT id, username, has_voted, created_at FROM users WHERE role = 'voter'")
    state = get_system_state()
    return render_template('admin_voters.html', voters=voters, state=state)

@app.route('/schedule_election', methods=['POST'])
@login_required(role='admin')
def schedule_election():
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    
    if start_time_str and end_time_str:
        # Convert from HTML datetime-local format (YYYY-MM-DDTHH:MM) to MySQL DATETIME (YYYY-MM-DD HH:MM:SS)
        start_time = start_time_str.replace('T', ' ') + ':00'
        end_time = end_time_str.replace('T', ' ') + ':00'
        
        db.execute_query("UPDATE system_state SET start_time = %s, end_time = %s WHERE id = 1", (start_time, end_time), commit=True)
        flash("Election scheduled successfully.", "success")
    else:
        flash("Start time and end time are required.", "error")
        
    return redirect(url_for('admin_schedule'))

@app.route('/admin/add_voter', methods=['POST'])
@login_required(role='admin')
def admin_add_voter():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    role = request.form.get('role', 'voter')
    
    if role not in ['admin', 'voter']:
        role = 'voter'
    
    # Check if username exists
    existing_user = db.execute_fetchone("SELECT id FROM users WHERE username = %s", (username,))
    if existing_user:
        flash("Username already exists", "error")
        return redirect(url_for('admin_voters'))

    hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    db.execute_query("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", (username, hashed, role), commit=True)
    flash(f"User '{username}' added successfully as {role}.", "success")
    return redirect(url_for('admin_voters'))

@app.route('/admin/modify_voter/<int:voter_id>', methods=['POST'])
@login_required(role='admin')
def admin_modify_voter(voter_id):
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    
    # Ensure voter exists
    voter = db.execute_fetchone("SELECT * FROM users WHERE id = %s AND role = 'voter'", (voter_id,))
    if not voter:
        flash("Voter not found.", "error")
        return redirect(url_for('admin_voters'))
        
    # Check username collision
    if new_username and new_username != voter['username']:
        existing_user = db.execute_fetchone("SELECT id FROM users WHERE username = %s", (new_username,))
        if existing_user:
            flash("Username already taken by another user.", "error")
            return redirect(url_for('admin_voters'))
            
    # Update logic
    if new_password:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute_query("UPDATE users SET username = %s, password_hash = %s WHERE id = %s", (new_username, hashed, voter_id), commit=True)
        flash(f"Voter '{new_username}' details and password updated successfully.", "success")
    else:
        db.execute_query("UPDATE users SET username = %s WHERE id = %s", (new_username, voter_id), commit=True)
        flash(f"Voter '{new_username}' username updated successfully.", "success")

    return redirect(url_for('admin_voters'))

@app.route('/admin/delete_voter/<int:voter_id>', methods=['POST'])
@login_required(role='admin')
def admin_delete_voter(voter_id):
    # Ensure voter exists
    voter = db.execute_fetchone("SELECT * FROM users WHERE id = %s AND role = 'voter'", (voter_id,))
    if not voter:
        flash("Voter not found.", "error")
        return redirect(url_for('admin_voters'))
        
    if voter['has_voted']:
        flash("Cannot delete a voter who has already cast a vote. This protects blockchain integrity.", "error")
        return redirect(url_for('admin_voters'))
        
    db.execute_query("DELETE FROM users WHERE id = %s", (voter_id,), commit=True)
    flash(f"Voter '{voter['username']}' deleted successfully.", "success")
    return redirect(url_for('admin_voters'))

@app.route('/add_candidate', methods=['POST'])
@login_required(role='admin')
def add_candidate():
    name = request.form['name']
    description = request.form['description']
    image_url = request.form['image_url'] or f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&size=150"
    
    db.execute_query(
        "INSERT INTO candidates (name, description, image_url) VALUES (%s, %s, %s)",
        (name, description, image_url),
        commit=True
    )
    flash("Candidate added successfully.", "success")
    return redirect(url_for('admin_schedule'))

@app.route('/results')
def results():
    state = get_system_state()
    
    # Restrict public results until election is complete
    if not state['end_time'] or datetime.now() <= state['end_time']:
        flash("Results are hidden. They will be visible only after the election is completed.", "error")
        return redirect(url_for('index'))
    
    # Calculate results securely from the blockchain
    # First verify the blockchain
    votes = db.execute_query("SELECT * FROM votes ORDER BY id ASC")
    is_valid, msg = Blockchain.verify_chain(votes)

    if not is_valid:
        flash(f"Blockchain integrity compromised! {msg}", "error")
        return render_template('results.html', valid=False, candidates=[])

    # Tally votes (excluding genesis block)
    tally = db.execute_query("""
        SELECT c.name, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
    """)

    return render_template('results.html', valid=True, results=tally)

@app.route('/api/blockchain_status')
def api_blockchain_status():
    votes = db.execute_query("SELECT * FROM votes ORDER BY id ASC")
    is_valid, msg = Blockchain.verify_chain(votes)
    return jsonify({"valid": is_valid, "message": msg, "total_blocks": len(votes)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
