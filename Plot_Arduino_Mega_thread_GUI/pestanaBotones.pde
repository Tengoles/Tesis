void actionPerformed (GUIEvent e) {
  if (e.getSource() == pauseButton) 
  {
    getdata.suspend();
    background(255, 255, 100);
  } else if (e.getSource() == resumeButton) 
  {
    myPort.clear();
    getdata.resume();
    background(100, 155, 100);
  } else if (e.getSource() == POsButton) 
  {
    myPort.write('4');
  } else if (e.getSource() == derivButton) 
  {
    deriv++;
    if (deriv == 4)
      deriv=1;

    if (deriv == 1)
    {
      myPort.write('1');
    } else if (deriv ==2)
    {
      myPort.write('2');
    } else if (deriv ==3)
    {
      myPort.write('3');
    }
  }
}
