CREATE DATABASE FCI
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Prefix VARCHAR(30) NOT NULL,
    ParentID INT ,
    Email VARCHAR(150) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Priority INT NOT NULL,
    FOREIGN KEY (ParentID) REFERENCES Users(UserID) ON DELETE SET NULL
);

CREATE TABLE Tasks (
    TaskID INT PRIMARY KEY AUTO_INCREMENT,
    TaskDescription TEXT NOT NULL,
    AssignedBy INT NOT NULL,
    AssignedTo INT NOT NULL,
    Status ENUM('Pending', 'Done') DEFAULT 'Pending',
    CreationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Deadline DATETIME NOT NULL,
    FOREIGN KEY (AssignedBy) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (AssignedTo) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE TABLE Requests (
    RequestID INT PRIMARY KEY AUTO_INCREMENT,
    RequestDescription TEXT NOT NULL,
    SentBy INT NOT NULL,
    SentTo INT NOT NULL,
    Status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    RequestDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SentBy) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (SentTo) REFERENCES Users(UserID) ON DELETE CASCADE
);

INSERT INTO Users (Name, Role, Prefix, ParentID, Email, Password, Priority)
VALUES ('Ali', 'Admin', 'IT', NULL, 'admin@it.com', 'pbkdf2:sha256:600000$o1inp7vOzppEoQqs$a894447ecbe355c71bf158a386551ed508d3ace66e74e177eed8e42b769ab250', 7);
