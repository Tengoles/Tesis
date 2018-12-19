import processing.serial.*;
import grafica.*;
import interfascia.*;
import controlP5.*; 

public GPlot plotECG, plotPO;//armo los plots (objeto)

ControlP5 cp5; 
ScrollableList portList;

GPointsArray pECG = new GPointsArray(500);
GPointsArray pPO = new GPointsArray(500);

GUIController c;
IFButton pauseButton, resumeButton, POsButton, derivButton, restartButton;

Serial myPort;  // Create object from Serial class

getData getdata = new getData();


boolean running;

PrintWriter fECG;//creo el objeto tipo txt
PrintWriter fPO;//creo el objeto tipo txt

String val;     // Data received from the serial port

byte[] Val = new byte[3];

long tiempo;
long tiempoInit;
long mInf=0;
long mSup=5000;

int tDato;
int vDato;
int iVal;
int cVal;
int deriv=1;

void setup()
{
  // I know that the first port in the serial list on my mac
  // is Serial.list()[0].
  // On Windows machines, this generally opens COM1.
  // Open whatever port is the one you're using.
  //String portName = Serial.list()[0]; //change the 0 to a 1 or 2 etc. to match your port

  //Creo la pantalla a presentar los datos
  size(1024, 768);
  frameRate(60);

  //creo el GUI
  c = new GUIController (this);

  // initiate cp5-library
  cp5 = new ControlP5(this); 

  pauseButton = new IFButton ("PAUSE", 512-50, 710, 90, 30);
  resumeButton = new IFButton ("RESUME", 512+50, 710, 90, 30);
  POsButton = new IFButton ("PO state", 512-150, 710, 90, 30);
  derivButton = new IFButton ("Derivacion", 512+150, 710, 90, 30);
  restartButton = new IFButton ("REINICIAR", 512+250, 710, 90, 30);

  pauseButton.addActionListener(this);
  resumeButton.addActionListener(this);
  POsButton.addActionListener(this);
  derivButton.addActionListener(this);
  restartButton.addActionListener(this);


  c.add (pauseButton);
  c.add (resumeButton);
  c.add (POsButton);
  c.add (derivButton);
  c.add (restartButton);


  // Setup for the ECG plot 
  plotECG = new GPlot(this);
  plotECG.setPos(0, 0);
  plotECG.setDim(930, 250);
  plotECG.setXLim(0, 5000);  
  plotECG.getTitle().setText("ECG data");
  plotECG.getXAxis().getAxisLabel().setText("Tiempo (ms)");
  plotECG.getYAxis().getAxisLabel().setText("Señal");

  // Draw the ECG plot  
  plotECG.beginDraw();
  plotECG.drawBackground();
  plotECG.drawBox();
  plotECG.drawXAxis();
  plotECG.drawYAxis();
  plotECG.drawTitle();
  plotECG.drawGridLines(GPlot.BOTH);
  plotECG.drawLines();
  plotECG.endDraw();

  // Setup for the PO plot 
  plotPO = new GPlot(this);
  plotPO.setPos(0, 350);
  plotPO.setDim(930, 250);
  plotPO.setXLim(0, 5000);
  plotPO.getTitle().setText("PO data");
  plotPO.getXAxis().getAxisLabel().setText("Tiempo (ms)");
  plotPO.getYAxis().getAxisLabel().setText("Señal");

  // Draw the PO plot  
  plotPO.beginDraw();
  plotPO.drawBackground();
  plotPO.drawBox();
  plotPO.drawXAxis();
  plotPO.drawYAxis();
  plotPO.drawTitle();
  plotPO.drawGridLines(GPlot.BOTH);
  plotPO.drawLines();
  plotPO.endDraw();

  //creo los archivo efectivamente
  fECG = createWriter("datosECG.txt");
  fPO = createWriter("datosPO.txt");

  //guardo el tiempo inicial
  tiempoInit = System.currentTimeMillis();

  String[] portNames =Serial.list(); 
  portList = cp5.addScrollableList("COM Port") 
    .setPosition(10, 10) 
    .setSize(200, 100) 
    .setBarHeight(20) 
    .setItemHeight(20) 
    .addItems(portNames) 
    .setValue(0);

  //abro puerto con arduino
  myPort = new Serial(this, "COM24", 9600);
  myPort.clear();
  getdata.start();
  background(255);
}

void draw()
{

  if (mSup<tiempo)
  {
    mSup=tiempo;
    mInf=mSup-5000;
  }

  try
  {
    // Draw the ECG plot  
    plotECG.beginDraw();
    plotECG.drawBackground();
    plotECG.drawBox();
    plotECG.setXLim(mInf-2000, mSup+2000);
    plotECG.setLineWidth(5);
    plotECG.drawXAxis();
    plotECG.drawYAxis();
    plotECG.drawTitle();
    plotECG.drawGridLines(GPlot.BOTH);
    plotECG.setPoints(pECG);
    plotECG.drawLines();
    plotECG.endDraw();
  }
  catch(NullPointerException e) {
    //me cabe
  }

  try 
  {
    // Draw the PO plot  
    plotPO.beginDraw();
    plotPO.drawBackground();
    plotPO.drawBox();
    plotPO.setXLim(mInf-2000, mSup+2000); 
    plotPO.setLineWidth(5);
    plotPO.drawXAxis();
    plotPO.drawYAxis();
    plotPO.drawTitle();
    plotPO.drawGridLines(GPlot.BOTH);
    plotPO.setPoints(pPO);
    plotPO.drawLines();
    plotPO.endDraw();
  }
  catch(NullPointerException e) {
    //me cabe
  }
}
